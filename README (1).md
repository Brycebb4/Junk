# Tri-State Junk Removal - Lead Generation & Business Website

A professional junk removal service website with integrated lead management system for the Cincinnati, Dayton, and Northern Kentucky areas.

![Junk Removal Cincinnati](https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=800&q=80)

## Features

### Customer Website (`index.html`)
- **Professional Landing Page**: Modern, responsive design optimized for conversions
- **Service Areas**: Cincinnati, Dayton (OH) and Covington, Northern Kentucky
- **Pricing Tiers**: Starting at $175, with clear pricing for different load sizes
- **Lead Capture Form**: Integrated contact form with localStorage (can be connected to email services)
- **SEO Optimized**: Keywords for local junk removal searches
- **Mobile Responsive**: Works perfectly on all devices

### Lead Management Dashboard (`dashboard.html`)
- **Lead Tracking**: Manually track leads from external sources (Craigslist, Facebook Marketplace, Nextdoor, etc.)
- **Auto-Categorization**: Automatically classifies leads as:
  - **Target ($175-$300)**: Your ideal price range
  - **High Value ($300+)**: Premium opportunities
  - **Too Low (<$175)**: May not be worth your time
- **Statistics Dashboard**: Real-time view of your lead pipeline
- **Filter & Search**: Filter by price range, status, and more
- **Contact Tracking**: Mark leads as contacted, pending, or won

## Getting Started

### Option 1: Deploy to GitHub Pages (Free)

1. **Create a GitHub Account** if you don't have one
2. **Create a New Repository**:
   - Go to github.com and click "New Repository"
   - Name it: `tri-state-junk-removal`
   - Make it Public
   - Click "Create Repository"

3. **Upload Files**:
   - Click "Add file" → "Upload files"
   - Upload `index.html` and `dashboard.html`
   - Click "Commit changes"

4. **Enable GitHub Pages**:
   - Go to Repository Settings
   - Click "Pages" on the left sidebar
   - Under "Branch", select `main` (or `master`)
   - Click Save
   - Your site will be live at: `https://yourusername.github.io/tri-state-junk-removal/`

### Option 2: Local Development

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/tri-state-junk-removal.git
   ```

2. Open `index.html` in your browser to view the website
3. Open `dashboard.html` in your browser to manage leads

## Lead Generation Strategy

### Where to Find Leads

1. **Cincinnati Craigslist** - Search "junk removal" "haul" "furniture removal"
2. **Facebook Marketplace** - Look for "free" items that need pickup
3. **Nextdoor** - Neighborhood requests for hauling services
4. **Angie's List / Thumbtack** - Home service lead platforms
5. **Google Local Searches** - Optimize your Google Business Profile

### Target Pricing

| Category | Price Range | Description |
|----------|-------------|-------------|
| Minimum | $175 | Single items (couch, mattress, appliance) |
| Target | $175-$300 | Small loads, garage cleanouts |
| Medium | $400-$600 | Half truck loads |
| Premium | $600-$1000+ | Full home cleanouts, construction debris |

### Best Practices

- **Respond Quickly**: Lead response time should be under 15 minutes
- **Ask for Photos**: Request photos of items to give accurate quotes
- **Same-Day Service**: Offer same-day pickup for extra value
- **Bundle Jobs**: Combine multiple small jobs in the same area

## Customization

### Update Contact Information

Edit `index.html` to update your business phone and email:

```html
<!-- Find and replace these sections -->
<a href="tel:+15555555555">(555) 555-5555</a>
<!-- And -->
info@tristatehaul.com
```

### Change Business Name

Search for "TRI-STATE HAUL" in the HTML and replace with your business name.

### Connect to Email Service

To receive email notifications when customers submit the form:

1. Sign up for a free account at [Formspree](https://formspree.io)
2. Create a new form and get your endpoint URL
3. Replace the form submission JavaScript in `index.html` with:

```javascript
form.action = "YOUR_FORMSPREE_ENDPOINT";
form.method = "POST";
```

## Technical Details

- **Framework**: Plain HTML/CSS/JavaScript (no build tools required)
- **Styling**: Tailwind CSS (via CDN)
- **Icons**: Font Awesome (via CDN)
- **Fonts**: Oswald & Roboto (Google Fonts)
- **Storage**: Browser localStorage (data persists in your browser)

## License

This project is for demonstration purposes. Feel free to use and modify for your own business.

---

**Note**: This website uses localStorage to store leads in your browser. For production use, we recommend connecting to a proper backend service or email provider.

**Created for Tri-State Junk Removal** | Cincinnati | Dayton | Northern Kentucky
