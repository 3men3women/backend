#!/usr/bin/env python
"""Django admin 등록 상태 확인 스크립트"""
import os
import sys
import django

# Django 설정
sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'testemo.settings')
django.setup()

from django.apps import apps
from django.contrib import admin

print("=== Django 모델 vs Admin 등록 상태 ===\n")

for app_config in apps.get_app_configs():
    if app_config.name in ['emodia', 'profiles', 'users']:
        print(f"\n📦 {app_config.name}")
        models = app_config.get_models()

        for model in models:
            model_name = model.__name__
            is_registered = model in admin.site._registry

            status = "✅ 등록됨" if is_registered else "❌ 미등록"
            print(f"  {model_name}: {status}")

            # 테이블에 데이터가 있는지 확인
            try:
                count = model.objects.count()
                if count > 0:
                    print(f"    → 데이터 {count}개 존재")
            except Exception as e:
                print(f"    → 데이터 조회 실패: {e}")
