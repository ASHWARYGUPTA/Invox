#!/bin/bash
# Gmail App Password Setup Checker
# Verifies all prerequisites for Gmail IMAP authentication

echo "=================================================="
echo "Gmail IMAP Authentication Checker"
echo "=================================================="
echo ""

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "This script will guide you through setting up Gmail IMAP"
echo "with App Passwords for the Invox application."
echo ""
echo "Press Enter to continue..."
read

echo ""
echo "Step 1: Check Python and Required Modules"
echo "=================================================="

if command -v python3 &> /dev/null; then
    echo -e "${GREEN}✓${NC} Python 3 is installed"
    python3 --version
else
    echo -e "${RED}✗${NC} Python 3 not found"
    exit 1
fi

echo ""
echo "Checking imaplib module..."
python3 -c "import imaplib; print('✓ imaplib available')" 2>/dev/null
if [ $? -ne 0 ]; then
    echo -e "${RED}✗${NC} imaplib not available"
    exit 1
fi

echo ""
echo "Step 2: Gmail Account Prerequisites"
echo "=================================================="
echo ""
echo "Please verify the following in your Gmail account:"
echo ""
echo "1. 2-Step Verification (2FA) is ENABLED"
echo "   Check at: https://myaccount.google.com/security"
echo "   ${YELLOW}Without 2FA, App Passwords won't work!${NC}"
echo ""
echo "2. IMAP is ENABLED in Gmail settings"
echo "   Check at: Gmail → Settings → Forwarding and POP/IMAP"
echo "   ${YELLOW}IMAP must be enabled to receive emails via API${NC}"
echo ""
echo "3. You have generated an App Password"
echo "   Generate at: https://myaccount.google.com/apppasswords"
echo "   ${YELLOW}App Password is 16 characters (remove spaces!)${NC}"
echo ""
echo "Have you completed all 3 prerequisites? (yes/no)"
read -r prerequisites

if [[ "$prerequisites" != "yes" ]]; then
    echo ""
    echo -e "${YELLOW}Please complete the prerequisites first:${NC}"
    echo ""
    echo "→ Step 1: Enable 2-Step Verification"
    echo "  https://myaccount.google.com/signinoptions/two-step-verification"
    echo ""
    echo "→ Step 2: Enable IMAP in Gmail"
    echo "  Gmail → Settings (gear) → See all settings → Forwarding and POP/IMAP"
    echo "  Select 'Enable IMAP' → Save Changes"
    echo ""
    echo "→ Step 3: Generate App Password"
    echo "  https://myaccount.google.com/apppasswords"
    echo "  Select app: Mail"
    echo "  Select device: Other (Custom name) → Enter 'Invox'"
    echo "  Click Generate → Copy the 16-character password"
    echo ""
    exit 0
fi

echo ""
echo "Step 3: Test IMAP Connection"
echo "=================================================="
echo ""
echo "Running IMAP connection test..."
echo ""

cd "$(dirname "$0")"

if [ -f "test_gmail_imap.py" ]; then
    python3 test_gmail_imap.py
    TEST_RESULT=$?
    
    if [ $TEST_RESULT -eq 0 ]; then
        echo ""
        echo -e "${GREEN}=================================================="
        echo "✓ IMAP Connection Test PASSED"
        echo "==================================================${NC}"
        echo ""
        echo "Your Gmail credentials work correctly!"
        echo ""
        echo "Next steps:"
        echo "1. Open Invox dashboard: http://localhost:3000/dashboard"
        echo "2. Click 'Configure Email'"
        echo "3. Enter the SAME credentials you just tested"
        echo "4. Click 'Test Connection' → Should show green checkmark"
        echo "5. Click 'Save Configuration'"
        echo "6. Email polling will start automatically"
        echo ""
    else
        echo ""
        echo -e "${RED}=================================================="
        echo "✗ IMAP Connection Test FAILED"
        echo "==================================================${NC}"
        echo ""
        echo "Common solutions:"
        echo ""
        echo "1. ${YELLOW}Wrong Password Type${NC}"
        echo "   ✗ Don't use your regular Gmail password"
        echo "   ✓ Must use 16-character App Password"
        echo "   Generate at: https://myaccount.google.com/apppasswords"
        echo ""
        echo "2. ${YELLOW}Spaces in Password${NC}"
        echo "   ✗ abcd efgh ijkl mnop (has spaces)"
        echo "   ✓ abcdefghijklmnop (no spaces)"
        echo ""
        echo "3. ${YELLOW}2FA Not Enabled${NC}"
        echo "   App Passwords require 2-Step Verification"
        echo "   Enable at: https://myaccount.google.com/security"
        echo ""
        echo "4. ${YELLOW}IMAP Not Enabled${NC}"
        echo "   Gmail → Settings → Forwarding and POP/IMAP"
        echo "   Select 'Enable IMAP' → Save Changes"
        echo ""
        echo "5. ${YELLOW}Old/Revoked App Password${NC}"
        echo "   Generate a fresh App Password"
        echo "   Revoke old ones at: https://myaccount.google.com/apppasswords"
        echo ""
    fi
else
    echo -e "${RED}✗${NC} test_gmail_imap.py not found"
    echo "Please ensure you're in the backend2 directory"
    exit 1
fi

echo ""
echo "Step 4: Backend Status Check"
echo "=================================================="
echo ""

if pgrep -f "uvicorn.*app.main:app" > /dev/null; then
    echo -e "${GREEN}✓${NC} Backend server is running"
    echo ""
    echo "Backend URL: http://localhost:8000"
    echo "API Docs: http://localhost:8000/docs"
else
    echo -e "${YELLOW}⚠${NC} Backend server is NOT running"
    echo ""
    echo "To start backend:"
    echo "  cd backend2"
    echo "  python -m uvicorn app.main:app --reload --port 8000"
fi

echo ""
echo "Step 5: Frontend Status Check"
echo "=================================================="
echo ""

if pgrep -f "next-server" > /dev/null || pgrep -f "node.*next" > /dev/null; then
    echo -e "${GREEN}✓${NC} Frontend server is running"
    echo ""
    echo "Dashboard: http://localhost:3000/dashboard"
else
    echo -e "${YELLOW}⚠${NC} Frontend server is NOT running"
    echo ""
    echo "To start frontend:"
    echo "  pnpm dev"
    echo "  # or npm run dev"
fi

echo ""
echo "=================================================="
echo "Setup Check Complete"
echo "=================================================="
echo ""

if [ $TEST_RESULT -eq 0 ]; then
    echo -e "${GREEN}✓ All checks passed!${NC}"
    echo ""
    echo "You're ready to configure email in Invox:"
    echo "1. Go to: http://localhost:3000/dashboard"
    echo "2. Click 'Configure Email' button"
    echo "3. Fill in your Gmail credentials"
    echo "4. Click 'Test Connection'"
    echo "5. Save configuration"
    echo ""
else
    echo -e "${YELLOW}⚠ Please fix the issues above and try again${NC}"
    echo ""
fi
