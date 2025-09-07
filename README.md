# Poetry Blog with Obsidian Integration

A beautiful poetry blog built with Zola that automatically syncs with your Obsidian vault.

## Features

- 🎨 Elegant Gruvbox-themed design with smooth animations
- 📝 Automatic sync from Obsidian vault's `publish` folder
- 🚀 Fast static site generation with Zola
- 📱 Responsive design for all devices
- ⚡ Live reload during development

## Quick Start

1. **Install dependencies**:
   ```bash
   # Install uv (if not already installed)
   curl -LsSf https://astral.sh/uv/install.sh | sh
   
   # Install Zola
   brew install zola  # macOS
   # Or download from https://www.getzola.org/
   ```

2. **Build and serve the site**:
   ```bash
   # Sync from Obsidian and build
   uv run build.py --serve
   
   # Or specify custom vault path
   uv run build.py --vault /path/to/your/vault --serve
   ```

3. **Add poetry to your Obsidian vault**:
   - Create a folder named `publish` in your Obsidian vault
   - Add markdown files with your poetry
   - They'll automatically sync to the blog!

## Usage

### Manual Sync
```bash
# Sync once from Obsidian
uv run sync_obsidian.py

# Sync from specific vault
uv run sync_obsidian.py --vault /path/to/vault
```

### Watch Mode
```bash
# Watch Obsidian folder for changes (uses watchdog for efficient monitoring)
uv run sync_obsidian.py --watch

# Build with live sync watching
uv run build.py --watch-sync --serve
```

### Development
```bash
# Just serve the site (no sync)
zola serve

# Build for production
zola build
```

## File Structure

```
poetry_blog/
├── content/           # Poetry markdown files
├── templates/         # Zola templates
├── sass/             # Stylesheets (Gruvbox theme)
├── static/           # Static assets
├── sync_obsidian.py  # Obsidian sync script
├── build.py          # Build script
├── pyproject.toml    # Python project configuration
└── config.toml       # Zola configuration
```

## Obsidian Setup

1. Create a `publish` folder in your Obsidian vault
2. Write your poetry in markdown files inside this folder
3. The sync script will:
   - Convert Obsidian markdown to Zola format
   - Add proper frontmatter with titles and dates
   - Copy files to the `content/` directory
   - Use efficient file watching with the `watchdog` library

## Customization

### Colors
The theme uses CSS custom properties for easy color customization. Edit `sass/style.scss` to change the Gruvbox palette.

### Templates
- `templates/base.html` - Base layout
- `templates/index.html` - Home page with poem list
- `templates/page.html` - Individual poem pages

## Deployment

After building with `zola build`, deploy the `public/` directory to any static hosting service:
- GitHub Pages
- Netlify  
- Vercel
- Your own server