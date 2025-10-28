@echo off
echo 📱 Setting up Jumbo Mobile App...
echo.

echo Step 1: Installing Expo CLI globally...
npm install -g @expo/cli

echo.
echo Step 2: Navigating to mobile app directory...
cd jumbo-mobile

echo.
echo Step 3: Installing dependencies...
npm install

echo.
echo Step 4: Starting Expo development server...
echo 🚀 Your mobile app will start shortly!
echo 📱 Install Expo Go on your phone and scan the QR code
echo.
npx expo start

pause