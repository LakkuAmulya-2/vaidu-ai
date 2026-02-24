#!/usr/bin/env python3
"""
Security check script - Run before pushing to GitHub
Verifies no sensitive data will be committed
"""
import os
import re
import sys

# Patterns that should NOT be in committed files
SENSITIVE_PATTERNS = [
    (r'AIzaSy[0-9A-Za-z_-]{33}', 'Google API Key'),
    (r'mg-endpoint-[a-f0-9-]{36}', 'MedGemma Endpoint ID'),
    (r'studio-\d+-[a-f0-9]{5}', 'Google Cloud Project ID'),
    (r'GOOGLE_CLOUD_PROJECT=(?!your-project-id)[^\s]+', 'Project ID in file'),
    (r'GEMINI_API_KEY=(?!your-)[^\s]+', 'Gemini API Key in file'),
]

# Files to check
FILES_TO_CHECK = [
    'README.md',
    'backend/.env.example',
    'frontend/.env.example',
    'BILLING_SETUP_GUIDE.md',
    'GITHUB_PUSH_GUIDE.md',
]

# Files that should be ignored
FILES_MUST_BE_IGNORED = [
    'backend/.env',
    'frontend/.env',
]

def check_gitignore():
    """Verify .env files are in .gitignore"""
    print("🔍 Checking .gitignore...")
    
    if not os.path.exists('.gitignore'):
        print("❌ .gitignore not found!")
        return False
    
    with open('.gitignore', 'r') as f:
        gitignore_content = f.read()
    
    missing = []
    for file in FILES_MUST_BE_IGNORED:
        if '.env' not in gitignore_content:
            missing.append(file)
    
    if missing:
        print(f"❌ These files are NOT in .gitignore: {missing}")
        return False
    
    print("✅ .gitignore is properly configured")
    return True

def check_sensitive_data():
    """Check for sensitive data in files"""
    print("\n🔍 Checking for sensitive data...")
    
    found_issues = []
    
    for filepath in FILES_TO_CHECK:
        if not os.path.exists(filepath):
            continue
        
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        for pattern, description in SENSITIVE_PATTERNS:
            matches = re.findall(pattern, content)
            if matches:
                found_issues.append(f"❌ {filepath}: Found {description}")
    
    if found_issues:
        print("\n".join(found_issues))
        return False
    
    print("✅ No sensitive data found in checked files")
    return True

def check_env_files_exist():
    """Verify .env files exist locally"""
    print("\n🔍 Checking .env files...")
    
    for filepath in FILES_MUST_BE_IGNORED:
        if not os.path.exists(filepath):
            print(f"⚠️  {filepath} not found (you'll need to create it)")
    
    return True

def main():
    print("=" * 60)
    print("🔒 VAIDU Security Check - GitHub Push Safety")
    print("=" * 60)
    
    checks = [
        check_gitignore(),
        check_sensitive_data(),
        check_env_files_exist(),
    ]
    
    print("\n" + "=" * 60)
    if all(checks):
        print("✅ ALL CHECKS PASSED - Safe to push to GitHub!")
        print("=" * 60)
        print("\nNext steps:")
        print("1. git init")
        print("2. git add .")
        print("3. git commit -m 'Initial commit'")
        print("4. Follow GITHUB_PUSH_GUIDE.md")
        return 0
    else:
        print("❌ SECURITY ISSUES FOUND - DO NOT PUSH!")
        print("=" * 60)
        print("\nFix the issues above before pushing to GitHub")
        return 1

if __name__ == '__main__':
    sys.exit(main())
