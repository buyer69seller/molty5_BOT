"""
Account setup — First-Run Intake per setup.md.
Generates Agent EOA, creates account, persists credentials.
Supports both interactive (local) and non-interactive (Railway/Docker) modes.

IMPORTANT: On Railway, env vars persist across restarts but dev-agent/ does not.
If env vars already have credentials (API_KEY, AGENT_PRIVATE_KEY, etc),
we restore from them instead of generating new wallets.
"""
import os
import sys
import asyncio
from bot.api_client import MoltyAPI, APIError
from bot.credentials import (
    is_first_run, save_credentials, save_owner_intake,
    save_agent_wallet, save_owner_wallet, load_credentials,
    load_agent_wallet, load_owner_wallet, update_env_file,
)
from bot.web3.wallet_manager import generate_agent_wallet, generate_owner_wallet
from bot.config import ADVANCED_MODE, AGENT_NAME, OWNER_EOA
from bot.utils.logger import get_logger

log = get_logger(__name__)


import asyncio
import json
import math
import requests
import websockets

# Konfigurasi Endpoint
AGENT_NAME = "buy6_9sell"
BASE_API_URL = "https://cdn.clawroyale.ai/api"
WS_JOIN_URL = "wss://cdn.clawroyale.ai/ws/join"
API_KEY = "mr_live_5uFKB4CBSSaWNpbxpWaiyOteqg3JRhy2"

# Parameter AI & Rejoin
LOW_HP_THRESHOLD = 0.4  # Pemicu Heal jika HP < 40%
RECONNECT_DELAY = 3     # Waktu tunggu sebelum auto-rejoin (detik)


def get_distance(pos1, pos2):
    """Menghitung jarak Euclidean antara dua titik koordinat."""
    dx = pos1.get("x", 0) - pos2.get("x", 0)
    dy = pos1.get("y", 0) - pos2.get("y", 0)
    return math.hypot(dx, dy)


def calculate_next_action(data):
    """
    AI Logic dengan urutan prioritas:
    1. Keluar dari Death Zone
    2. Heal jika HP Rendah
    3. Serang Monster Terdekat
    """
    player = data.get("player", data.get("self", {}))
    position = player.get("position", {"x": 0, "y": 0})
    hp = player.get("hp", 100)
    max_hp = player.get("maxHp", 100)

    # -------------------------------------------------------------
    # PRIORITAS 1: Keluar dari Death Zone (Safe Zone Check)
    # -------------------------------------------------------------
    safe_zone = data.get("safeZone", data.get("zone", {}))
    if safe_zone:
        center = safe_zone.get("center", {"x": 0, "y": 0})
        radius = safe_zone.get("radius", 1000)
        dist_to_center = get_distance(position, center)

        # Jika berada di dekat atau di luar batas lingkaran safe zone
        if dist_to_center > (radius * 0.8):
            return {
                "type": "action",
                "action": "move",
                "target": center
            }

    # -------------------------------------------------------------
    # PRIORITAS 2: Heal jika HP Rendah
    # -------------------------------------------------------------
    if (hp / max_hp) < LOW_HP_THRESHOLD:
        skills = player.get("skills", [])
        # Opsi A: Gunakan skill Heal jika tersedia
        if "heal" in skills:
            return {
                "type": "action",
                "action": "use_skill",
                "skill": "heal"
            }
        
        # Opsi B: Bergerak menuju item Heal/Medkit terdekat jika ada di map
        heal_items = data.get("healItems", [])
        if heal_items:
            nearest_heal = min(heal_items, key=lambda h: get_distance(position, h.get("position", {})))
            return {
                "type": "action",
                "action": "move",
                "target": nearest_heal.get("position")
            }

    # -------------------------------------------------------------
    # PRIORITAS 3: Serang Monster Terdekat
    # -------------------------------------------------------------
    monsters = data.get("monsters", data.get("entities", []))
    if monsters:
        nearest_monster = min(monsters, key=lambda m: get_distance(position, m.get("position", {})))
        monster_pos = nearest_monster.get("position", {})
        dist_to_monster = get_distance(position, monster_pos)
        attack_range = player.get("attackRange", 50)

        # Serang jika dalam jangkauan, atau mendekat jika di luar jangkauan
        if dist_to_monster <= attack_range:
            return {
                "type": "action",
                "action": "attack",
                "targetId": nearest_monster.get("id")
            }
        else:
            return {
                "type": "action",
                "action": "move",
                "target": monster_pos
            }

    # Gerakan default jika tidak ada ancaman/monster: bergerak mendekati safe zone center
    return {
        "type": "action",
        "action": "move",
        "target": safe_zone.get("center", {"x": 0, "y": 0}) if safe_zone else {"x": 0, "y": 0}
    }


async def play_claw_royale():
    try:
        response = requests.get(f"{BASE_API_URL}/version", timeout=5)
        version_data = response.json()
        current_version = version_data.get("version", "1.15.0")
    except Exception as e:
        print(f"Gagal mengambil versi: {e}")
        return

    headers = {
        "X-Version": current_version,
        "X-API-Key": API_KEY
    }

    print(f"Menghubungkan ke {WS_JOIN_URL} dengan versi {current_version}...")

    async with websockets.connect(WS_JOIN_URL, additional_headers=headers) as ws:
        welcome_frame = await ws.recv()
        print(f"Welcome Frame: {welcome_frame}")

        hello_payload = {
            "type": "hello",
            "entryType": "free"
        }
        await ws.send(json.dumps(hello_payload))
        print("Hello payload terkirim. Menunggu event permainan...")

        async for message in ws:
            event = json.loads(message)
            event_type = event.get("type")

            # Cek jika agen mati atau game selesai
            if event_type == "agent_died":
                meta = event.get("meta", {})
                if meta.get("youDied") is True:
                    print("Agen mati! Menyiapkan Auto Rejoin...")
                    break
            elif event_type == "game_ended":
                print("Permainan selesai! Menyiapkan Auto Rejoin...")
                break

            # Eksekusi aksi saat menerima kabar agent_view / game_state
            elif event_type in ["agent_view", "game_state"]:
                view_data = event.get("data", event)
                action_payload = calculate_next_action(view_data)
                
                if action_payload:
                    await ws.send(json.dumps(action_payload))


async def main():
    """Loop Utama dengan sistem Auto Rejoin."""
    while True:
        try:
            await play_claw_royale()
        except websockets.exceptions.ConnectionClosed as e:
            print(f"Koneksi terputus: {e}")
        except Exception as e:
            print(f"Terjadi kesalahan: {e}")

        print(f"Rejoining dalam {RECONNECT_DELAY} detik...\n")
        await asyncio.sleep(RECONNECT_DELAY)


if __name__ == "__main__":
    asyncio.run(main())
