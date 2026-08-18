"""
Script de teste do ambiente DEEP-AUREA
Valida que Python, uv, ripgrep e bibliotecas essenciais estÃ£o operacionais.
"""
import sys
import os
import subprocess
import platform
import json
import math
import re
import collections
import datetime
import pathlib

def test_python():
    print(f"[OK] Python {sys.version}")
    return True

def test_uv():
    try:
        result = subprocess.run(["uv", "--version"], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print(f"[OK] uv {result.stdout.strip()}")
            return True
        else:
            print(f"[FAIL] uv erro: {result.stderr}")
            return False
    except FileNotFoundError:
        print("[FAIL] uv nÃ£o encontrado no PATH")
        return False

def test_rg():
    # PossÃ­veis locais do rg
    rg_candidates = [
        "rg",
        "C:\\Users\\User\\rg\\ripgrep-14.1.0-x86_64-pc-windows-msvc\\rg.exe",
        "C:\\Users\\User\\.local\\bin\\rg.exe",
    ]
    for rg_path in rg_candidates:
        try:
            result = subprocess.run([rg_path, "--version"], capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                first_line = result.stdout.strip().split("\n")[0]
                print(f"[OK] {first_line}")
                return True
        except (FileNotFoundError, OSError):
            continue
    print("[FAIL] rg nÃ£o encontrado em nenhum local conhecido")
    return False

def test_imports():
    try:
        # Verifica se os mÃ³dulos estÃ£o acessÃ­veis
        for mod in [math, os, json, re, collections, datetime, pathlib, subprocess]:
            pass
        print("[OK] ImportaÃ§Ãµes bÃ¡sicas funcionando")
        return True
    except Exception as e:
        print(f"[FAIL] Erro de importaÃ§Ã£o: {e}")
        return False

def test_file_operations():
    try:
        test_path = os.path.join(os.path.dirname(__file__), ".test_write")
        with open(test_path, "w") as f:
            f.write("test")
        with open(test_path, "r") as f:
            content = f.read()
        os.remove(test_path)
        assert content == "test"
        print("[OK] OperaÃ§Ãµes de arquivo (leitura/escrita/remoÃ§Ã£o)")
        return True
    except Exception as e:
        print(f"[FAIL] OperaÃ§Ãµes de arquivo: {e}")
        return False

def test_json():
    try:
        data = {"name": "DEEP-AUREA", "status": "operational"}
        encoded = json.dumps(data)
        decoded = json.loads(encoded)
        assert decoded == data
        print("[OK] JSON serializaÃ§Ã£o/desserializaÃ§Ã£o")
        return True
    except Exception as e:
        print(f"[FAIL] JSON: {e}")
        return False

def main():
    print("=" * 60)
    print(" TESTE DO AMBIENTE DEEP-AUREA")
    print("=" * 60)
    print(f"Plataforma: {platform.platform()}")
    print(f"MÃ¡quina: {platform.machine()}")
    print(f"Sistema: {platform.system()} {platform.release()}")
    print("-" * 60)

    tests = [
        ("Python", test_python),
        ("uv", test_uv),
        ("ripgrep", test_rg),
        ("ImportaÃ§Ãµes", test_imports),
        ("Arquivos", test_file_operations),
        ("JSON", test_json),
    ]

    results = []
    for name, func in tests:
        try:
            result = func()
        except Exception as e:
            print(f"[FAIL] {name}: exceÃ§Ã£o: {e}")
            result = False
        results.append(result)

    print("-" * 60)
    success = all(results)
    total = len(results)
    passed = sum(results)
    print(f"Resultado: {passed}/{total} testes passaram")
    if success:
        print("[OK] Ambiente 100% operacional no Windows!")
    else:
        print("[FAIL] Alguns testes falharam. Verifique as mensagens acima.")
    print("=" * 60)

    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
