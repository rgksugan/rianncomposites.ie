# Riann Composites — website

Static [Jekyll](https://jekyllrb.com/) site for **Riann Composites**, fiberglass &
carbon fiber repair specialists (Tulla, Co. Clare, Ireland). Built to deploy on
**GitHub Pages**.

## Structure

```
_config.yml              # site + business details (phone, email, WhatsApp…)
_layouts/default.html    # page shell
_includes/               # head, topbar, header, footer
index.html               # one-page landing (hero, services, results, etc.)
contact.html             # contact page + enquiry form
404.html
assets/css/style.css     # all styles
assets/js/main.js        # nav, sticky header, counters, before/after slider
assets/images/           # logo + favicon
.github/workflows/       # GitHub Pages build & deploy
```

## Editing content

Most business details (phone, email, WhatsApp number, address) live in one place —
the `business:` block in [`_config.yml`](_config.yml). Change them there and they
update everywhere on the site.

## Contact form

The contact form posts to [Formspree](https://formspree.io). To receive enquiries:

1. Create a free Formspree account and a new form.
2. Copy your form ID and set `formspree_id` in `_config.yml`.

Until then, WhatsApp / phone / email links work without any setup.

## Deploying to GitHub Pages

1. Create a GitHub repo and push this folder to the `main` branch.
2. In **Settings → Pages**, set **Source = GitHub Actions**.
   The included workflow ([`.github/workflows/jekyll.yml`](.github/workflows/jekyll.yml))
   builds and deploys automatically on every push to `main`.

### Project page vs custom domain

- **Custom domain** (e.g. `rianncomposites.ie`) or user page: leave
  `baseurl: ""` in `_config.yml`. Add a `CNAME` file with your domain and configure
  it under Settings → Pages.
- **Project page** served at `https://USERNAME.github.io/REPO/`: the workflow passes
  the correct base path automatically at build time, so links/assets resolve.

## Running locally

**With Ruby/Jekyll** (recommended, matches production):

```bash
bundle install
bundle exec jekyll serve
# http://localhost:4000
```

**Without Ruby** — a tiny preview renderer is included for quick design checks
(it covers only the small Liquid subset this site uses):

```bash
python3 preview_build.py
python3 -m http.server 8765 --directory _preview
# http://localhost:8765
```

`preview_build.py` and `_preview/` are for local preview only and are excluded from
the real Jekyll build.
