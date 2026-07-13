# Image Prompts for MedInsight Landing Page

## Hero Section Illustration (Line 272)
**Context**: Right side of hero, on dark teal (#0e384c) background, rounded 3xl, aspect ratio 4:3
**Purpose**: Convey medical intelligence, data analytics, clinical decision support

### Prompt
```
A modern, flat-style isometric illustration of a medical analytics dashboard. Shows a doctor's tablet or screen displaying patient vitals (heart rate, blood pressure graphs, lab results), surrounded by floating medical icons: stethoscope, DNA helix, clipboard with checkboxes, and a small patient avatar. Color palette: teal (#0e384c), light blue (#1e84b5), white, and subtle green accents. Clean, minimal, professional healthcare SaaS style. No text. White/transparent background.
```

### Style Notes
- Flat design, not photorealistic
- Isometric or slight 3D perspective
- Teal/blue dominant colors matching the site theme
- Suitable for dark background (use white/light elements)
- No words or letters (will be overlaid with CSS)

---

## About Section Illustration (Line 370)
**Context**: Right side of "About" section, on light gray (#f9fcff) background, rounded 3xl, aspect ratio 1:1.1
**Purpose**: Convey medical team collaboration, patient care, trust





### Prompt
```
A warm, modern flat illustration of a diverse medical team collaborating around a digital patient file. Shows 2-3 doctors in white coats, one pointing at a large tablet or screen displaying patient data, with a subtle heartbeat line or medical chart in the background. Soft teal (#0e384c) and blue (#1e84b5) color palette with warm skin tones. Friendly, approachable, professional healthcare SaaS aesthetic. No text. Light gray or white background.
```

### Style Notes
- Flat design with soft gradients
- Warm, inviting feel (represents "About Us" trust section)
- Teal/blue palette with natural skin tones
- Suitable for light background
- No words or letters

---

## Usage Notes
1. Generate images at 2x resolution (e.g., 800x600 for hero, 600x660 for about)
2. Save as `C:\Users\WAB\3D Objects\Projects\Mm Projet MED\img` and `public/about-illustration.png`
3. Update `src/pages/landing/index.tsx` to use `<img>` tags instead of `<ImagePlaceholder>`
4. Ensure images are optimized (< 200KB each) for fast loading
5. Test on both desktop and mobile viewports


