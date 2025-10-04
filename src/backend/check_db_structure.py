#!/usr/bin/env python
"""DB 테이블 및 컬럼명 확인 스크립트"""
import os
import sys
import django

# Django 설정
sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'testemo.settings')
django.setup()

from django.db import connection

print("=== 데이터베이스 테이블 및 컬럼명 ===\n")

with connection.cursor() as cursor:
    cursor.execute("SHOW TABLES;")
    tables = cursor.fetchall()

    for table in tables:
        table_name = table[0]
        if 'emodia' in table_name or 'profiles' in table_name:
            print(f"\n📋 테이블: {table_name}")

            cursor.execute(f"DESCRIBE {table_name};")
            columns = cursor.fetchall()

            for col in columns:
                col_name = col[0]
                col_type = col[1]
                print(f"   - {col_name} ({col_type})")
