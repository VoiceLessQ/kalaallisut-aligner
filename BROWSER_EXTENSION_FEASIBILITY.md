# Browser Extension Feasibility Analysis

## Executive Summary

**Verdict: FEASIBLE with limitations**

A browser extension can be created from this project, but will require significant architectural changes. The most practical approach is a **hybrid extension** combining offline dictionary lookup with optional server-side morphological analysis.

## Current Project Architecture

### Core Components
1. **Glosser** (glosser_v2_fixed.py) - Morpheme-by-morpheme analysis
2. **Morphological Analyzer** (preprocessor.py) - Uses lang-kal HFST tools
3. **Sentence Aligner** (align_production.sh) - Uses hunalign binary
4. **Dictionaries**:
   - Kalaallisut-English: 16,819 entries (837KB)
   - Morpheme glosses: 67 entries (1.5KB)
   - Danish-Kalaallisut cognates: 1,526 pairs (41KB)

### Technical Dependencies
- **Language**: Python 3
- **External Tools**:
  - `hfst-tokenize` (HFST tokenizer)
  - `hfst-lookup` (morphological analyzer)
  - `hunalign` (sentence alignment)
- **Libraries**: pandas, odfpy
- **System Requirements**: Compiled binaries (lang-kal, hunalign)

## Critical Challenges

### 1. System Dependencies ⚠️
**Problem**: The project relies on compiled C/C++ binaries that cannot run in browsers:
- `hfst-tokenize` (from HFST/lang-kal)
- `hfst-lookup` (morphological analyzer)
- `hunalign` (alignment tool)

**Impact**: Morphological analysis (`preprocessor.py`) cannot function as-is in browser.

### 2. Python Runtime ⚠️
**Problem**: Browser extensions use JavaScript/TypeScript, not Python.

**Solutions**:
- Rewrite in JavaScript (significant effort)
- Use Pyodide (Python in WebAssembly) - adds 10-20MB overhead
- Build backend API (requires server hosting)

### 3. Subprocess Calls 🚫
**Problem**: `preprocessor.py` uses `subprocess.run()` to call external binaries.

**Browser Limitation**: No subprocess support in browsers.

### 4. File System Access ⚠️
**Problem**: Project reads from local filesystem extensively.

**Browser Limitation**: Limited filesystem access, requires bundling data or using IndexedDB.

## Feasible Approaches

### ⭐ Approach 1: Hybrid Extension (RECOMMENDED)

**Architecture**:
```
Browser Extension (JavaScript)
├── Offline Features
│   ├── Dictionary lookup (16,819 entries)
│   ├── Word highlighting on web pages
│   ├── Basic glossing (no morphological analysis)
│   └── Cognate matching (1,526 pairs)
└── Online Features (Optional)
    ├── API call to backend server
    ├── Full morphological analysis
    └── Advanced glossing
```

**Implementation**:
1. **Extension Frontend** (JavaScript):
   - Bundle dictionaries as JSON in extension
   - Implement word lookup and simple translation
   - Add context menu for "Translate Kalaallisut"
   - Highlight Kalaallisut words on web pages
   - Show popup with translations

2. **Backend API** (Python - Optional):
   - Deploy existing Python code as REST API
   - Handle morphological analysis requests
   - Can be self-hosted or cloud-hosted

**Pros**:
- Works offline for basic translations ✅
- Preserves most functionality ✅
- Can upgrade to full features when online ✅
- Moderate development effort ✅

**Cons**:
- Advanced features require internet ⚠️
- Need to maintain two codebases ⚠️
- Backend hosting costs (if using API) ⚠️

**Dictionary Size**: ~880KB (acceptable for extension)

---

### Approach 2: WebAssembly + Pyodide (ADVANCED)

**Architecture**:
```
Browser Extension
├── Pyodide (Python runtime in WASM) - ~20MB
├── HFST tools compiled to WASM
├── Python code (existing)
└── Dictionaries
```

**Implementation**:
1. Compile HFST tools to WebAssembly
2. Load Pyodide in extension background script
3. Run existing Python code in browser
4. Bundle all data files

**Pros**:
- Full functionality offline ✅
- No backend needed ✅
- Preserves existing codebase ✅

**Cons**:
- Very large extension size (20-50MB) 🚫
- Complex build process 🚫
- Slow initialization time ⚠️
- HFST compilation to WASM may be difficult 🚫

**Not recommended** due to complexity and size constraints.

---

### Approach 3: JavaScript Rewrite (SIMPLIFIED)

**Architecture**:
```
Browser Extension (Pure JavaScript)
├── Simple dictionary lookup
├── Basic tokenization (regex-based)
├── No morphological analysis
└── UI for web page translation
```

**Implementation**:
1. Rewrite glosser in JavaScript
2. Implement simple word splitting (no HFST)
3. Bundle dictionaries as JSON
4. Create browser extension UI

**Pros**:
- Small size (~1-2MB) ✅
- Fast and lightweight ✅
- Works completely offline ✅
- Simple to maintain ✅

**Cons**:
- No morphological analysis 🚫
- Limited accuracy without HFST 🚫
- Loss of advanced features 🚫

**Good for**: MVP or simple translation tool

---

### Approach 4: Backend API Only (CLIENT-SERVER)

**Architecture**:
```
Browser Extension (Thin Client)
    ↓
Backend API (Python + HFST)
    ↓
Full functionality
```

**Implementation**:
1. Minimal JavaScript extension (UI only)
2. All processing on backend server
3. Send text via API, receive glossed output

**Pros**:
- Full functionality ✅
- Small extension size ✅
- Reuses existing code 100% ✅

**Cons**:
- Requires internet connection always 🚫
- Privacy concerns (sending text to server) 🚫
- Hosting costs ⚠️
- Latency on each request ⚠️

---

## Recommended Implementation Plan

### Phase 1: MVP - Offline Dictionary Extension

**Features**:
- [x] Bundle Kalaallisut-English dictionary (837KB)
- [x] Bundle cognates dictionary (41KB)
- [x] Implement word lookup in JavaScript
- [x] Add context menu: "Translate Kalaallisut word"
- [x] Show popup with translation
- [x] Highlight Kalaallisut words on web pages (optional)

**Tech Stack**:
- Manifest V3 browser extension
- Vanilla JavaScript or TypeScript
- Chrome + Firefox support

**Effort**: 1-2 weeks for experienced developer

---

### Phase 2: Enhanced Features

**Add**:
- Danish-Kalaallisut translation (using cognates)
- In-page translation overlay
- Settings panel (enable/disable features)
- Export translations
- History of lookups

**Effort**: 1-2 weeks additional

---

### Phase 3: API Integration (Optional)

**Add**:
- Backend API deployment (Python Flask/FastAPI)
- Optional morphological analysis via API
- User can toggle offline/online mode
- Show morpheme breakdown when online

**Effort**: 1-2 weeks for API + deployment

---

## Feature Comparison Matrix

| Feature | Current Project | Hybrid Extension | WebAssembly | JS Rewrite | API Only |
|---------|----------------|------------------|-------------|------------|----------|
| Dictionary Lookup | ✅ | ✅ | ✅ | ✅ | ✅ |
| Morphological Analysis | ✅ | ⚠️ (API) | ✅ | 🚫 | ✅ |
| Sentence Alignment | ✅ | 🚫 | ⚠️ | 🚫 | ✅ |
| Offline Support | ✅ | ✅ | ✅ | ✅ | 🚫 |
| Size | N/A | ~2MB | ~30MB | ~1MB | <1MB |
| Development Effort | N/A | Medium | Very High | Low | Low |
| Maintenance | N/A | Medium | High | Low | Medium |

✅ Fully supported | ⚠️ Partially/conditionally supported | 🚫 Not supported

---

## Technical Specifications for Hybrid Extension

### Extension Structure
```
kalaallisut-extension/
├── manifest.json                 # Extension manifest (V3)
├── background.js                 # Service worker
├── content/
│   ├── content.js               # Injected into web pages
│   └── content.css              # Styling for highlights
├── popup/
│   ├── popup.html               # Extension popup UI
│   ├── popup.js
│   └── popup.css
├── data/
│   ├── kal_eng_dict.json        # 16,819 entries (837KB)
│   ├── cognates.json            # 1,526 pairs (41KB)
│   └── morpheme_glosses.json    # 67 entries (1.5KB)
├── lib/
│   ├── translator.js            # Core translation logic
│   └── api.js                   # Optional API client
└── options/
    ├── options.html             # Settings page
    └── options.js
```

### Core Features

**1. Context Menu Integration**
```javascript
// Right-click selected text → "Translate from Kalaallisut"
chrome.contextMenus.create({
  title: "Translate from Kalaallisut",
  contexts: ["selection"]
});
```

**2. Dictionary Lookup**
```javascript
class KalaallisutTranslator {
  constructor() {
    this.dictionary = null; // Loaded from data/kal_eng_dict.json
  }

  translate(word) {
    // Exact match
    if (this.dictionary[word]) {
      return this.dictionary[word];
    }

    // Case-insensitive match
    const lower = word.toLowerCase();
    if (this.dictionary[lower]) {
      return this.dictionary[lower];
    }

    // Try removing common suffixes (basic stemming)
    return this.tryStemming(word);
  }
}
```

**3. In-Page Highlighting**
```javascript
// Scan page for Kalaallisut words
function highlightKalaallisutWords() {
  const walker = document.createTreeWalker(
    document.body,
    NodeFilter.SHOW_TEXT
  );

  // Find and highlight words in dictionary
  while (walker.nextNode()) {
    const node = walker.currentNode;
    const words = node.textContent.split(/\s+/);
    // Highlight words found in dictionary
  }
}
```

**4. Optional API Integration**
```javascript
// For advanced morphological analysis
async function getMorphologicalAnalysis(word) {
  if (!settings.apiEnabled) {
    return null;
  }

  const response = await fetch(`${API_URL}/analyze`, {
    method: 'POST',
    body: JSON.stringify({ word }),
    headers: { 'Content-Type': 'application/json' }
  });

  return response.json();
}
```

### Browser Compatibility
- **Chrome/Edge**: Full support (Manifest V3)
- **Firefox**: Full support (Manifest V3)
- **Safari**: Requires conversion to Safari extension format

### Data Loading Strategy
```javascript
// Load dictionaries on extension install
chrome.runtime.onInstalled.addListener(async () => {
  // Load dictionaries into memory or IndexedDB
  const dict = await fetch(chrome.runtime.getURL('data/kal_eng_dict.json'));
  const dictData = await dict.json();

  // Store in chrome.storage.local or keep in memory
  await chrome.storage.local.set({ dictionary: dictData });
});
```

---

## Use Cases for Browser Extension

### 1. Reading Greenlandic Websites
**Scenario**: User visits Greenlandic news site (e.g., sermitsiaq.ag)

**Workflow**:
1. User highlights unknown Kalaallisut word
2. Right-click → "Translate from Kalaallisut"
3. Popup shows English translation + morpheme breakdown (if API enabled)

### 2. Learning Kalaallisut
**Scenario**: Language learner reading Kalaallisut texts

**Workflow**:
1. Extension automatically highlights known/unknown words
2. Hover over word to see quick translation
3. Click for detailed morphological analysis

### 3. Translation Assistance
**Scenario**: Translator working on Danish-Kalaallisut documents

**Workflow**:
1. Extension provides cognate suggestions
2. Quick lookup for terminology
3. Export translation notes

---

## Privacy & Security Considerations

### Data Handling
- ✅ All dictionaries bundled locally (no external requests for offline mode)
- ✅ No tracking or analytics
- ⚠️ API mode: user text sent to server (need privacy policy)

### Permissions Required
```json
{
  "permissions": [
    "activeTab",           // Access current page
    "contextMenus",        // Right-click menu
    "storage"              // Store dictionaries
  ],
  "optional_permissions": [
    "https://api.example.com/*"  // For API features
  ]
}
```

### Content Security Policy
- No inline scripts
- Only load resources from extension package
- API calls only to whitelisted domains

---

## Development Estimates

### MVP (Phase 1)
- **Setup & Architecture**: 2 days
- **Dictionary Integration**: 2 days
- **Context Menu & Popup**: 3 days
- **Testing & Polish**: 2 days
- **Documentation**: 1 day
- **Total**: ~2 weeks

### Enhanced Version (Phase 2)
- **In-page Highlighting**: 3 days
- **Settings Panel**: 2 days
- **Enhanced UI**: 3 days
- **Total**: +1.5 weeks

### API Integration (Phase 3)
- **Backend API**: 4 days
- **Frontend Integration**: 2 days
- **Deployment Setup**: 2 days
- **Total**: +1.5 weeks

**Full Project**: 5 weeks for complete implementation

---

## Costs & Resources

### Development
- **One-time**: $5,000 - $15,000 (depending on features)
- **Maintenance**: $500 - $1,000/month (if using API backend)

### Hosting (if using API)
- **Server**: $10-50/month (small VPS)
- **Domain**: $10-20/year
- **SSL Certificate**: Free (Let's Encrypt)

### Distribution
- **Chrome Web Store**: $5 one-time fee
- **Firefox Add-ons**: Free
- **Edge Add-ons**: Free

---

## Limitations of Browser Extension

### What CAN be implemented:
✅ Dictionary lookup (16,819 entries)
✅ Word-by-word translation
✅ Cognate matching (Danish-Kalaallisut)
✅ Basic glossing (without morphology)
✅ In-page highlighting
✅ Export translations

### What CANNOT be implemented (without API):
🚫 Full morphological analysis (requires HFST)
🚫 Sentence alignment (requires hunalign)
🚫 Complex tokenization (requires HFST tokenizer)
🚫 Processing of aligned corpora

### Workarounds:
- Simple regex-based tokenization (less accurate)
- Basic suffix stripping (limited)
- API calls for advanced features (requires internet)

---

## Alternatives to Consider

### 1. Progressive Web App (PWA)
Instead of browser extension, create a web application:
- **Pros**: Works on all devices, easier updates
- **Cons**: Not integrated with web browsing, requires separate tab

### 2. Desktop Application (Electron)
Port to desktop app with full Python backend:
- **Pros**: Full functionality, no limitations
- **Cons**: Not integrated with browser, larger download

### 3. Mobile App
Create iOS/Android app:
- **Pros**: Portable, touch-friendly
- **Cons**: Different use case than browser extension

---

## Conclusion

**YES, a browser extension is feasible**, but with important limitations:

### Best Approach: Hybrid Extension
1. **Offline mode**: Dictionary lookup, basic translation (good for 80% of use cases)
2. **Online mode**: Full morphological analysis via API (for advanced users)
3. **Size**: ~2MB (reasonable)
4. **Development effort**: Moderate (5-6 weeks)

### Key Trade-offs:
- ✅ Maintains core value (translation lookup)
- ⚠️ Loses advanced morphological analysis (unless API used)
- 🚫 Cannot do sentence alignment in browser
- ✅ Better user experience for casual lookup
- ⚠️ Requires rewrite from Python to JavaScript

### Recommendation:
**BUILD IT** if the primary use case is:
- Helping people read Kalaallisut text on websites
- Quick word lookup and translation
- Learning aid for language students

**DON'T BUILD IT** if you need:
- Full morphological analysis without internet
- Sentence alignment
- Processing large corpora
- Research-grade accuracy

For most users wanting to read Greenlandic websites, the hybrid extension would be **extremely valuable** and technically feasible.

---

## Next Steps

If proceeding with development:

1. **Validate assumptions**:
   - Survey potential users
   - Determine offline vs. API usage preference
   - Identify most-needed features

2. **Prototype MVP** (1 week):
   - Basic dictionary lookup
   - Context menu integration
   - Simple popup UI

3. **User testing**:
   - Test with Kalaallisut learners
   - Gather feedback on accuracy
   - Iterate on UX

4. **Production build**:
   - Add remaining features
   - Polish UI/UX
   - Submit to Chrome Web Store / Firefox Add-ons

---

**Date**: November 2025
**Analysis by**: Claude
**Project**: Kalaallisut-Danish Sentence Aligner → Browser Extension
