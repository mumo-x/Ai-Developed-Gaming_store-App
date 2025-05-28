# Installation Guide for Trinix Gaming Shop

## For Users

### Windows Installation

1. Download the latest installer (.exe) from the releases page
2. Run the installer
3. Follow the on-screen instructions to complete the installation
4. The application will be available in your Start menu and as a desktop shortcut

### Uninstallation

1. Go to Control Panel > Programs > Programs and Features
2. Find "Trinix Gaming Shop" in the list
3. Click "Uninstall" and follow the prompts
4. Alternatively, you can use the uninstaller in the installation directory

## For Developers

### Building the Installer

1. Make sure you have Node.js installed
2. Clone the repository
3. Install dependencies:
   ```
   npm install
   ```
4. Build the application:
   ```
   npm run build
   ```
5. The installer will be created in the `dist` folder

### Customizing the Installer

You can customize the installer by modifying the `build` section in `package.json`. Options include:

- Changing the application name
- Modifying installation directory
- Adding/removing shortcuts
- Customizing the installer UI

For more options, refer to the [electron-builder documentation](https://www.electron.build/).