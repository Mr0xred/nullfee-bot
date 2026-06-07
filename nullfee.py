import asyncio
import aiohttp
import json
import random
import time
import os

# ============== CONFIG ==============
BASE_URL = "https://nullfee.io/api"
PASSWORD = "@Masuk123"
CLIENT_FP = "2560x1440|Asia/Bangkok|id-ID|6"

HEADERS_BASE = {
    "sec-ch-ua-platform": '"Windows"',
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36",
    "sec-ch-ua": '"Chromium";v="148", "Brave";v="148", "Not/A)Brand";v="99"',
    "sec-ch-ua-mobile": "?0",
    "content-type": "application/json",
    "origin": "https://nullfee.io",
    "referer": "https://nullfee.io/register/",
}

FIRST_NAMES = [
    "andi", "budi", "citra", "dewi", "eko", "fajar", "gita", "hadi",
    "indra", "joko", "kartika", "lina", "mira", "nanda", "oki", "putra",
    "ratna", "sari", "tono", "udin", "vina", "wati", "yanto", "zaki",
    "agus", "bambang", "cahya", "dian", "endang", "fitri", "gunawan",
    "hendra", "irfan", "joni", "kiki", "lukman", "maya", "nina",
    "oscar", "pandu", "rini", "surya", "tika", "utami", "vera",
    "wahyu", "yuli", "zahra", "arif", "bayu", "deni", "elsa",
    "fandi", "galih", "hana", "imam", "jaya", "karin", "luki",
    "maman", "nisa", "opik", "prima", "reza", "sinta", "taufik",
    "umi", "vivi", "wawan", "yogi", "zul", "adit", "bima",
    "candra", "dimas", "erna", "farhan", "gilang", "haris", "ilham",
    "jihan", "kevin", "laras", "mulia", "nabil", "okta", "pras",
    "rizky", "sandi", "tegar", "umar", "valdo", "wisnu", "xander",
    "yuda", "zain", "alif", "bagus", "chandra", "dafa", "evan",
]

SWAP_PAIRS = [
    {"fromChain": "bsc", "toChain": "ethereum", "fromToken": "USDT", "toToken": "USDT"},
    {"fromChain": "ethereum", "toChain": "bsc", "fromToken": "USDT", "toToken": "USDT"},
    {"fromChain": "bsc", "toChain": "ethereum", "fromToken": "BNB", "toToken": "USDT"},
    {"fromChain": "ethereum", "toChain": "bsc", "fromToken": "USDT", "toToken": "BNB"},
    {"fromChain": "bsc", "toChain": "polygon", "fromToken": "USDT", "toToken": "USDT"},
    {"fromChain": "polygon", "toChain": "bsc", "fromToken": "USDT", "toToken": "USDT"},
    {"fromChain": "ethereum", "toChain": "polygon", "fromToken": "USDT", "toToken": "USDT"},
    {"fromChain": "polygon", "toChain": "ethereum", "fromToken": "USDT", "toToken": "USDT"},
    {"fromChain": "bsc", "toChain": "optimism", "fromToken": "USDT", "toToken": "USDT"},
    {"fromChain": "optimism", "toChain": "bsc", "fromToken": "USDT", "toToken": "USDT"},
    {"fromChain": "bsc", "toChain": "arbitrum", "fromToken": "USDT", "toToken": "USDT"},
    {"fromChain": "arbitrum", "toChain": "bsc", "fromToken": "USDT", "toToken": "USDT"},
    {"fromChain": "bsc", "toChain": "base", "fromToken": "USDT", "toToken": "USDT"},
    {"fromChain": "base", "toChain": "bsc", "fromToken": "USDT", "toToken": "USDT"},
    {"fromChain": "ethereum", "toChain": "ton", "fromToken": "USDT", "toToken": "USDT"},
    {"fromChain": "polygon", "toChain": "ton", "fromToken": "USDT", "toToken": "USDT"},
    {"fromChain": "polygon", "toChain": "bitcoin", "fromToken": "USDT", "toToken": "BTC"},
    {"fromChain": "polygon", "toChain": "solana", "fromToken": "USDT", "toToken": "SOL"},
    {"fromChain": "polygon", "toChain": "avalanche", "fromToken": "USDT", "toToken": "USDT"},
    {"fromChain": "bsc", "toChain": "ethereum", "fromToken": "USDC", "toToken": "ETH"},
    {"fromChain": "ethereum", "toChain": "bitcoin", "fromToken": "USDT", "toToken": "BTC"},
    {"fromChain": "bitcoin", "toChain": "bsc", "fromToken": "BTC", "toToken": "BNB"},
    {"fromChain": "base", "toChain": "arbitrum", "fromToken": "ETH", "toToken": "USDT"},
]

results = []
bnb_results = []
lock = asyncio.Lock()

# Counter untuk progress
counter = {"success": 0, "fail": 0, "total": 0}


def generate_username():
    name = random.choice(FIRST_NAMES)
    number = random.randint(1, 99999)
    return f"{name}{number}"


async def register_and_spin(session, ref_code, sem):
    """Register satu akun + mystery box spin, dengan semaphore untuk limit concurrency"""
    async with sem:
        username = generate_username()
        payload = {
            "username": username,
            "password": PASSWORD,
            "ref": ref_code,
            "clientFp": CLIENT_FP,
        }

        try:
            # Register
            async with session.post(
                f"{BASE_URL}/auth/register",
                json=payload,
                headers={**HEADERS_BASE, "referer": f"https://nullfee.io/register/?ref={ref_code}"},
                timeout=aiohttp.ClientTimeout(total=20),
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if "user" not in data:
                        counter["fail"] += 1
                        print(f"  [-] Register gagal: {username} - {data.get('message', data)}")
                        return
                elif resp.status == 429:
                    # Rate limited, retry setelah delay
                    await asyncio.sleep(random.uniform(2, 5))
                    counter["fail"] += 1
                    return
                else:
                    counter["fail"] += 1
                    text = await resp.text()
                    print(f"  [-] Register {resp.status}: {username} - {text[:80]}")
                    return

            # Cookies sudah di-set otomatis oleh aiohttp CookieJar
            # Langsung spin mystery box
            await asyncio.sleep(random.uniform(0.5, 1.5))

            spin_headers = {**HEADERS_BASE, "referer": "https://nullfee.io/mystery-box"}
            async with session.post(
                f"{BASE_URL}/mystery-box/spin",
                json={"daily": True},
                headers=spin_headers,
                timeout=aiohttp.ClientTimeout(total=20),
            ) as resp:
                mb_data = None
                got_bnb = False
                if resp.status == 200:
                    mb_data = await resp.json()
                    if mb_data.get("ok"):
                        prize = mb_data.get("prize", {})
                        label = mb_data.get("label", "")
                        kind = prize.get("kind", "")
                        currency = prize.get("currency", "")
                        amount = prize.get("amount", 0)
                        got_bnb = "bnb" in kind.lower() or currency.upper() == "BNB"

                        if got_bnb:
                            print(f"  [$$] BNB! {username}: {label}")

            result_entry = {
                "username": username,
                "password": PASSWORD,
                "mysteryBox": {
                    "label": mb_data.get("label", "") if mb_data else "",
                    "kind": mb_data.get("prize", {}).get("kind", "") if mb_data else "",
                    "currency": mb_data.get("prize", {}).get("currency", "") if mb_data else "",
                    "amount": mb_data.get("prize", {}).get("amount", 0) if mb_data else 0,
                    "gotBnb": got_bnb,
                } if mb_data and mb_data.get("ok") else None,
            }

            async with lock:
                results.append(result_entry)
                if got_bnb:
                    bnb_results.append(result_entry)

            counter["success"] += 1

        except asyncio.TimeoutError:
            counter["fail"] += 1
        except Exception as e:
            counter["fail"] += 1
            print(f"  [-] Error {username}: {str(e)[:60]}")


async def progress_printer(total):
    """Print progress setiap 2 detik"""
    while counter["success"] + counter["fail"] < total:
        done = counter["success"] + counter["fail"]
        print(f"  [PROGRESS] {done}/{total} | OK: {counter['success']} | Fail: {counter['fail']} | BNB: {len(bnb_results)}", end="\r")
        await asyncio.sleep(2)
    print(f"  [DONE] {total}/{total} | OK: {counter['success']} | Fail: {counter['fail']} | BNB: {len(bnb_results)}          ")


async def run_register(ref_code, num_accounts, num_threads, proxy_list=None):
    """Jalankan register secara async"""
    sem = asyncio.Semaphore(num_threads)

    connector = aiohttp.TCPConnector(limit=num_threads, limit_per_host=num_threads)

    tasks = []
    progress_task = asyncio.create_task(progress_printer(num_accounts))

    for i in range(num_accounts):
        proxy_url = random.choice(proxy_list) if proxy_list else None
        task = asyncio.create_task(register_and_spin_wrapper(ref_code, sem, connector, proxy_url))
        tasks.append(task)

    # Tunggu semua selesai
    await asyncio.gather(*tasks, return_exceptions=True)

    progress_task.cancel()
    try:
        await progress_task
    except asyncio.CancelledError:
        pass

    await connector.close()


async def register_and_spin_wrapper(ref_code, sem, connector, proxy_url):
    """Wrapper yang handle proxy per-request"""
    async with sem:
        jar = aiohttp.CookieJar()
        kwargs_session = {"connector": connector, "cookie_jar": jar, "connector_owner": False}
        if proxy_url:
            kwargs_session["trust_env"] = True
            
        session = aiohttp.ClientSession(**kwargs_session)
        username = generate_username()
        payload = {
            "username": username,
            "password": PASSWORD,
            "ref": ref_code,
            "clientFp": CLIENT_FP,
        }

        try:
            # Register
            kwargs = {
                "json": payload,
                "headers": {**HEADERS_BASE, "referer": f"https://nullfee.io/register/?ref={ref_code}"},
                "timeout": aiohttp.ClientTimeout(total=20),
            }
            if proxy_url:
                kwargs["proxy"] = proxy_url

            async with session.post(f"{BASE_URL}/auth/register", **kwargs) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if "user" not in data:
                        counter["fail"] += 1
                        return
                elif resp.status == 429:
                    await asyncio.sleep(random.uniform(2, 4))
                    counter["fail"] += 1
                    return
                else:
                    counter["fail"] += 1
                    text = await resp.text()
                    print(f"  [-] Register {resp.status}: {username} - {text[:80]}")
                    return

            # Mystery box spin
            await asyncio.sleep(random.uniform(0.3, 1))

            kwargs2 = {
                "json": {"daily": True},
                "headers": {**HEADERS_BASE, "referer": "https://nullfee.io/mystery-box"},
                "timeout": aiohttp.ClientTimeout(total=20),
            }
            if proxy_url:
                kwargs2["proxy"] = proxy_url

            mb_data = None
            got_bnb = False

            async with session.post(f"{BASE_URL}/mystery-box/spin", **kwargs2) as resp:
                if resp.status == 200:
                    mb_data = await resp.json()
                    if mb_data.get("ok"):
                        prize = mb_data.get("prize", {})
                        kind = prize.get("kind", "")
                        currency = prize.get("currency", "")
                        got_bnb = "bnb" in kind.lower() or currency.upper() == "BNB"
                        if got_bnb:
                            print(f"  [$$] BNB! {username}: {mb_data.get('label', '')}")

            result_entry = {
                "username": username,
                "password": PASSWORD,
                "mysteryBox": {
                    "label": mb_data.get("label", "") if mb_data else "",
                    "kind": mb_data.get("prize", {}).get("kind", "") if mb_data else "",
                    "currency": mb_data.get("prize", {}).get("currency", "") if mb_data else "",
                    "amount": mb_data.get("prize", {}).get("amount", 0) if mb_data else 0,
                    "gotBnb": got_bnb,
                } if mb_data and mb_data.get("ok") else None,
            }

            async with lock:
                results.append(result_entry)
                if got_bnb:
                    bnb_results.append(result_entry)

            counter["success"] += 1

        except asyncio.TimeoutError:
            counter["fail"] += 1
            print(f"  [-] Timeout: {username}")
        except Exception as e:
            counter["fail"] += 1
            print(f"  [-] Error {username}: {type(e).__name__} {str(e)[:60]}")
            
        await session.close()


async def login_and_swap(account, sem, connector, proxy_url):
    """Login dan swap sampai saldo habis"""
    async with sem:
        username = account["username"]
        password = account["password"]

        jar = aiohttp.CookieJar()
        async with aiohttp.ClientSession(connector=connector, cookie_jar=jar) as session:
            # Login
            login_payload = {"username": username, "password": password}
            kwargs = {
                "json": login_payload,
                "headers": {**HEADERS_BASE, "referer": "https://nullfee.io/"},
                "timeout": aiohttp.ClientTimeout(total=20),
            }
            if proxy_url:
                kwargs["proxy"] = proxy_url

            try:
                async with session.post(f"{BASE_URL}/auth/login", **kwargs) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        if "user" not in data:
                            print(f"  [-] Login gagal: {username}")
                            return
                        user_data = data["user"]
                    else:
                        print(f"  [-] Login {resp.status}: {username}")
                        return
            except Exception as e:
                print(f"  [-] Login error {username}: {str(e)[:60]}")
                return

            balance = user_data.get("balanceUsdCents", 0)
            if balance < 500:
                print(f"  [!] Saldo kurang: {username} (${balance/100:.2f})")
                return

            print(f"  [+] Login OK: {username} | ${balance/100:.2f}")

            # Swap sampai habis
            swap_count = 0
            current_balance = balance

            while current_balance >= 500:
                pair = random.choice(SWAP_PAIRS)
                amount = 10 if current_balance >= 1000 and random.random() > 0.4 else 5

                swap_payload = {
                    "fromChain": pair["fromChain"],
                    "toChain": pair["toChain"],
                    "fromToken": pair["fromToken"],
                    "toToken": pair["toToken"],
                    "amountUsd": amount,
                }

                kwargs_swap = {
                    "json": swap_payload,
                    "headers": {**HEADERS_BASE, "referer": "https://nullfee.io/swap"},
                    "timeout": aiohttp.ClientTimeout(total=20),
                }
                if proxy_url:
                    kwargs_swap["proxy"] = proxy_url

                try:
                    async with session.post(f"{BASE_URL}/swap", **kwargs_swap) as resp:
                        if resp.status == 200:
                            sdata = await resp.json()
                            if sdata.get("ok"):
                                current_balance = sdata.get("balances", {}).get("usdCents", 0)
                                swap_count += 1
                                if swap_count % 10 == 0:
                                    print(f"  [~] {username}: {swap_count} swaps... (Sisa ${current_balance/100:.2f})")
                            else:
                                break
                        elif resp.status == 429:
                            await asyncio.sleep(random.uniform(2, 4))
                            continue
                        else:
                            break
                except Exception:
                    break

                await asyncio.sleep(random.uniform(0.5, 1.5))

            print(f"  [=] {username}: {swap_count} swaps done, sisa ${current_balance/100:.2f}")


async def run_daily_swap(accounts, num_threads, proxy_list=None):
    """Jalankan daily swap secara async"""
    sem = asyncio.Semaphore(num_threads)
    connector = aiohttp.TCPConnector(limit=num_threads, limit_per_host=num_threads)

    tasks = []
    for acc in accounts:
        proxy_url = random.choice(proxy_list) if proxy_list else None
        tasks.append(asyncio.create_task(login_and_swap(acc, sem, connector, proxy_url)))

    await asyncio.gather(*tasks, return_exceptions=True)
    await connector.close()


def save_results():
    """Simpan hasil ke file"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    result_path = os.path.join(script_dir, "result.json")
    bnb_path = os.path.join(script_dir, "bnbresult.txt")

    with open(result_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\n[*] Hasil disimpan ke result.json ({len(results)} akun)")

    if bnb_results:
        with open(bnb_path, "w") as f:
            for entry in bnb_results:
                mb = entry.get("mysteryBox", {})
                f.write(f"{entry['username']}:{entry['password']} | BNB Prize: {mb.get('label', '')} amount={mb.get('amount', 0)}\n")
        print(f"[*] BNB results disimpan ke bnbresult.txt ({len(bnb_results)} akun)")


def menu_register():
    print("\n" + "=" * 50)
    print("  MENU 1: REGISTER AKUN NULLFEE")
    print("=" * 50)

    ref_code = input("\n[?] Masukkan kode referral (Enter untuk default mr0xred_8208): ").strip()
    if not ref_code:
        ref_code = "mr0xred_8208"

    try:
        num_accounts = int(input("[?] Jumlah akun yang akan diregister: ").strip())
    except ValueError:
        print("[-] Input tidak valid!")
        return

    try:
        num_threads = int(input("[?] Jumlah threading (concurrent): ").strip())
    except ValueError:
        num_threads = 10

    proxy_list = []
    script_dir = os.path.dirname(os.path.abspath(__file__))
    proxies_path = os.path.join(script_dir, "proxies.txt")
    if os.path.exists(proxies_path):
        with open(proxies_path, "r") as f:
            proxy_list = [line.strip() for line in f if line.strip()]
        print(f"[*] Ditemukan {len(proxy_list)} proxy di proxies.txt, akan digunakan secara acak.")
    else:
        print("[*] Tidak ada proxies.txt, jalan tanpa proxy.")

    print(f"\n[*] Mulai register {num_accounts} akun | Concurrency: {num_threads}")
    print(f"[*] Referral: {ref_code}")
    print("-" * 50)

    start = time.time()

    # Reset counter
    counter["success"] = 0
    counter["fail"] = 0

    asyncio.run(run_register(ref_code, num_accounts, num_threads, proxy_list))

    elapsed = time.time() - start
    print(f"\n[*] Selesai dalam {elapsed:.1f} detik ({counter['success']}/{num_accounts} berhasil)")

    save_results()


def menu_daily_swap():
    print("\n" + "=" * 50)
    print("  MENU 2: DAILY SWAP")
    print("=" * 50)

    script_dir = os.path.dirname(os.path.abspath(__file__))
    result_path = os.path.join(script_dir, "result.json")

    if not os.path.exists(result_path):
        print("[-] File result.json tidak ditemukan! Register dulu.")
        return

    with open(result_path, "r") as f:
        accounts = json.load(f)

    if not accounts:
        print("[-] Tidak ada akun di result.json!")
        return

    print(f"[*] Ditemukan {len(accounts)} akun di result.json")

    try:
        num_threads = int(input("[?] Jumlah threading (concurrent): ").strip())
    except ValueError:
        num_threads = 10

    proxy_list = []
    proxies_path = os.path.join(script_dir, "proxies.txt")
    if os.path.exists(proxies_path):
        with open(proxies_path, "r") as f:
            proxy_list = [line.strip() for line in f if line.strip()]
        print(f"[*] Ditemukan {len(proxy_list)} proxy di proxies.txt, akan digunakan secara acak.")
    else:
        print("[*] Tidak ada proxies.txt, jalan tanpa proxy.")

    print(f"\n[*] Mulai daily swap | Concurrency: {num_threads}")
    print("-" * 50)

    start = time.time()
    asyncio.run(run_daily_swap(accounts, num_threads, proxy_list))
    elapsed = time.time() - start

    print(f"\n[*] Daily swap selesai dalam {elapsed:.1f} detik")


def main():
    print("""
+==========================================+
|        NULLFEE.IO AUTO BOT               |
|        Register & Daily Swap             |
+==========================================+
    """)

    while True:
        print("\n[1] Register Akun (+ Mystery Box)")
        print("[2] Daily Swap")
        print("[0] Exit")

        choice = input("\n[?] Pilih menu: ").strip()

        if choice == "1":
            menu_register()
        elif choice == "2":
            menu_daily_swap()
        elif choice == "0":
            print("\n[*] Bye!")
            break
        else:
            print("[-] Pilihan tidak valid!")


if __name__ == "__main__":
    main()
