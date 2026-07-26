# DRAFTRON UI Specification

## Table of Contents
1. [Overview](#overview)
2. [Brand Identity](#brand-identity)
3. [Color Palette](#color-palette)
4. [Typography](#typography)
5. [Layout Structure](#layout-structure)
6. [Page Components](#page-components)
7. [State Management](#state-management)
8. [Responsive Design](#responsive-design)
9. [Accessibility](#accessibility)
10. [Implementation Notes](#implementation-notes)

---

## Overview

DRAFTRON is an AI-powered cover letter generator with human-in-the-loop review. The UI should feel professional, efficient, and trustworthy — designed for job seekers who want quality output without spending hours writing.

### Design Principles
- **Clarity over decoration** — every element serves a purpose
- **Progressive disclosure** — show what's needed, when it's needed
- **Confidence building** — make the user trust the AI's output
- **Efficiency** — minimize clicks, maximize feedback loops

---

## Brand Identity

### Name
**DRAFTRON** — AI Cover Letter Agent

### Tagline
"Your AI-powered cover letter, reviewed by you"

### Logo Concept
- Minimalist, modern
- Suggests writing/document + AI
- Color: Primary blue (#2563EB)

### Voice & Tone
- Professional but approachable
- Confident, not arrogant
- Helpful, not patronizing

---

## Color Palette

### Primary Colors
```css
--primary-50: #eff6ff;    /* Lightest blue - backgrounds */
--primary-100: #dbeafe;   /* Light blue - hover states */
--primary-200: #bfdbfe;   /* Light blue - borders */
--primary-300: #93c5fd;   /* Medium blue - disabled states */
--primary-400: #60a5fa;   /* Medium blue - icons */
--primary-500: #3b82f6;   /* Primary blue - main actions */
--primary-600: #2563eb;   /* Primary blue - hover */
--primary-700: #1d4ed8;   /* Primary blue - active */
--primary-800: #1e40af;   /* Dark blue - text */
--primary-900: #1e3a8a;   /* Darkest blue - headings */
```

### Success Colors
```css
--success-50: #f0fdf4;    /* Light green - success bg */
--success-100: #dcfce7;   /* Light green - success border */
--success-500: #22c55e;   /* Green - success icon */
--success-600: #16a34a;   /* Green - success text */
--success-700: #15803d;   /* Dark green - success heading */
```

### Warning Colors
```css
--warning-50: #fffbeb;    /* Light yellow - warning bg */
--warning-100: #fef3c7;   /* Light yellow - warning border */
--warning-500: #f59e0b;   /* Yellow - warning icon */
--warning-600: #d97706;   /* Yellow - warning text */
--warning-700: #b45309;   /* Dark yellow - warning heading */
```

### Error Colors
```css
--error-50: #fef2f2;      /* Light red - error bg */
--error-100: #fee2e2;     /* Light red - error border */
--error-500: #ef4444;     /* Red - error icon */
--error-600: #dc2626;     /* Red - error text */
--error-700: #b91c1c;     /* Dark red - error heading */
```

### Neutral Colors
```css
--gray-50: #f9fafb;       /* Lightest gray - page bg */
--gray-100: #f3f4f6;      /* Light gray - card bg */
--gray-200: #e5e7eb;      /* Light gray - borders */
--gray-300: #d1d5db;      /* Medium gray - disabled */
--gray-400: #9ca3af;      /* Medium gray - placeholder text */
--gray-500: #6b7280;      /* Medium gray - secondary text */
--gray-600: #4b5563;      /* Dark gray - body text */
--gray-700: #374151;      /* Dark gray - headings */
--gray-800: #1f2937;      /* Dark gray - primary text */
--gray-900: #111827;      /* Darkest gray - high contrast text */
```

---

## Typography

### Font Stack
```css
--font-sans: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
--font-mono: 'JetBrains Mono', 'Fira Code', 'Cascadia Code', Consolas, monospace;
```

### Font Sizes
```css
--text-xs: 0.75rem;      /* 12px - captions, labels */
--text-sm: 0.875rem;     /* 14px - small text, metadata */
--text-base: 1rem;       /* 16px - body text */
--text-lg: 1.125rem;     /* 18px - subheadings */
--text-xl: 1.25rem;      /* 20px - section headings */
--text-2xl: 1.5rem;      /* 24px - page titles */
--text-3xl: 1.875rem;    /* 30px - hero text */
```

### Font Weights
```css
--font-normal: 400;      /* Body text */
--font-medium: 500;      /* Emphasis, buttons */
--font-semibold: 600;    /* Subheadings */
--font-bold: 700;        /* Headings */
```

---

## Layout Structure

### Page Layout
```
┌─────────────────────────────────────────────────────────────┐
│                        HEADER                               │
│  Logo | Title | Navigation                                  │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│                    MAIN CONTENT                             │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                  SIDEBAR (optional)                  │   │
│  │  - Pipeline progress                                │   │
│  │  - Application history                              │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                CONTENT AREA                          │   │
│  │  - Job posting input                                │   │
│  │  - Draft display                                    │   │
│  │  - Review interface                                 │   │
│  │  - Final letter                                     │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│                        FOOTER                               │
│  Status | Version | Links                                   │
└─────────────────────────────────────────────────────────────┘
```

### Grid System
- **Desktop:** 12-column grid, max-width 1200px, centered
- **Tablet:** 8-column grid, padding 24px
- **Mobile:** 4-column grid, padding 16px

### Spacing Scale
```css
--space-1: 0.25rem;      /* 4px */
--space-2: 0.5rem;       /* 8px */
--space-3: 0.75rem;      /* 12px */
--space-4: 1rem;         /* 16px */
--space-5: 1.25rem;      /* 20px */
--space-6: 1.5rem;       /* 24px */
--space-8: 2rem;         /* 32px */
--space-10: 2.5rem;      /* 40px */
--space-12: 3rem;        /* 48px */
--space-16: 4rem;        /* 64px */
```

---

## Page Components

### 1. Header

**Purpose:** Brand identity, navigation, status

**Components:**
- Logo (left)
- Title: "DRAFTRON" (left, next to logo)
- Tagline: "AI Cover Letter Agent" (right of title)
- Status indicator (right) — shows connection status

**Styling:**
```css
.header {
  background: white;
  border-bottom: 1px solid var(--gray-200);
  padding: var(--space-4) var(--space-6);
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  position: sticky;
  top: 0;
  z-index: 100;
}
```

---

### 2. Sidebar (Pipeline Progress)

**Purpose:** Show where the user is in the pipeline, display application history

**Components:**
- **Pipeline Steps:**
  1. Job Posting Input
  2. Profile Matching
  3. Draft Generation
  4. Self-Critique
  5. Human Review
  6. Finalization

- **Application History:**
  - List of recent applications
  - Company name, role, date, status
  - Click to view saved letter

**Styling:**
```css
.sidebar {
  background: var(--gray-50);
  border-right: 1px solid var(--gray-200);
  padding: var(--space-6);
  min-height: calc(100vh - 80px);
  width: 300px;
}

.pipeline-step {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-3);
  border-radius: 8px;
  margin-bottom: var(--space-2);
  transition: background 0.2s;
}

.pipeline-step.active {
  background: var(--primary-50);
  border-left: 3px solid var(--primary-500);
}

.pipeline-step.completed {
  background: var(--success-50);
  border-left: 3px solid var(--success-500);
}

.pipeline-step.pending {
  background: var(--gray-100);
  border-left: 3px solid var(--gray-300);
}
```

---

### 3. Job Posting Input (Step 1)

**Purpose:** Collect the job posting text from the user

**Components:**
- **Title:** "Paste Job Posting"
- **Subtitle:** "Copy the job description from the posting and paste it here"
- **Text Area:**
  - Placeholder: "Paste the full job posting here..."
  - Min height: 200px
  - Max height: 400px
  - Character count indicator
- **Generate Button:**
  - Text: "Generate Cover Letter"
  - Icon: Sparkles (✨) or Wand (🪄)
  - Color: Primary blue
  - Size: Large
  - Disabled until text is entered
- **Tips Section:**
  - Collapsible
  - Tips for better results:
    - Include the full job description
    - Include company name and role title
    - Include requirements and nice-to-haves

**Styling:**
```css
.input-section {
  background: white;
  border-radius: 12px;
  padding: var(--space-8);
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  border: 1px solid var(--gray-200);
}

.textarea {
  width: 100%;
  min-height: 200px;
  max-height: 400px;
  padding: var(--space-4);
  border: 2px solid var(--gray-200);
  border-radius: 8px;
  font-family: var(--font-sans);
  font-size: var(--text-base);
  line-height: 1.6;
  resize: vertical;
  transition: border-color 0.2s, box-shadow 0.2s;
}

.textarea:focus {
  border-color: var(--primary-500);
  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
  outline: none;
}

.generate-button {
  background: var(--primary-500);
  color: white;
  padding: var(--space-4) var(--space-8);
  border-radius: 8px;
  font-size: var(--text-lg);
  font-weight: var(--font-semibold);
  border: none;
  cursor: pointer;
  transition: background 0.2s, transform 0.1s;
  display: flex;
  align-items: center;
  gap: var(--space-2);
}

.generate-button:hover {
  background: var(--primary-600);
  transform: translateY(-1px);
}

.generate-button:active {
  background: var(--primary-700);
  transform: translateY(0);
}

.generate-button:disabled {
  background: var(--gray-300);
  cursor: not-allowed;
  transform: none;
}
```

---

### 4. Loading/Processing State

**Purpose:** Show progress while the AI is working

**Components:**
- **Spinner:** Animated loading indicator
- **Status Text:** "Analyzing job posting..." / "Matching skills..." / "Generating draft..."
- **Progress Bar:** Optional, for longer operations
- **Cancel Button:** To abort the current operation

**Styling:**
```css
.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: var(--space-12);
  text-align: center;
}

.spinner {
  width: 48px;
  height: 48px;
  border: 4px solid var(--gray-200);
  border-top: 4px solid var(--primary-500);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: var(--space-4);
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.progress-bar {
  width: 100%;
  max-width: 400px;
  height: 8px;
  background: var(--gray-200);
  border-radius: 4px;
  overflow: hidden;
  margin-top: var(--space-4);
}

.progress-fill {
  height: 100%;
  background: var(--primary-500);
  border-radius: 4px;
  transition: width 0.3s ease;
}
```

---

### 5. Draft Display & Critique (Step 4-5)

**Purpose:** Show the generated draft and self-critique results

**Components:**
- **Header:** "Your Draft Cover Letter"
- **Draft Display:**
  - Formatted text with paragraphs
  - Copy button (top right)
  - Word count indicator
- **Critique Section:**
  - Collapsible section
  - Status badge: Pass/Fail
  - Details:
    - Overstatement flags (if any)
    - Length flag (if any)
    - Tone flag (if any)
    - Notes from critique
  - Color coding: Green for pass, Red for fail, Yellow for warnings
- **Revision Count:** "Revisions: 0" (incremented on each edit)

**Styling:**
```css
.draft-container {
  background: white;
  border-radius: 12px;
  padding: var(--space-6);
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  border: 1px solid var(--gray-200);
  margin-bottom: var(--space-6);
}

.draft-text {
  font-family: var(--font-sans);
  font-size: var(--text-base);
  line-height: 1.8;
  color: var(--gray-800);
  white-space: pre-wrap;
}

.critique-section {
  background: var(--gray-50);
  border-radius: 8px;
  padding: var(--space-4);
  margin-top: var(--space-4);
}

.critique-badge {
  display: inline-flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-1) var(--space-3);
  border-radius: 9999px;
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
}

.critique-badge.pass {
  background: var(--success-100);
  color: var(--success-700);
}

.critique-badge.fail {
  background: var(--error-100);
  color: var(--error-700);
}

.flag-item {
  display: flex;
  align-items: flex-start;
  gap: var(--space-2);
  padding: var(--space-2) 0;
  border-bottom: 1px solid var(--gray-200);
}

.flag-item:last-child {
  border-bottom: none;
}

.flag-icon {
  color: var(--warning-500);
  flex-shrink: 0;
  margin-top: 2px;
}
```

---

### 6. Human Review Interface (Step 5)

**Purpose:** Allow user to approve, edit, regenerate, or reject the draft

**Components:**
- **Action Buttons:**
  - **Approve** (Primary, Green)
    - Icon: Checkmark (✓)
    - Text: "Approve & Finalize"
    - Saves the letter and logs the application
  - **Edit** (Secondary, Blue)
    - Icon: Pencil (✏️)
    - Text: "Request Edit"
    - Requires feedback in text area
  - **Regenerate** (Secondary, Yellow)
    - Icon: Refresh (🔄)
    - Text: "Regenerate"
    - Generates new draft with same strategy
  - **Reject** (Danger, Red)
    - Icon: X (✕)
    - Text: "Reject"
    - Discards the draft, ends pipeline

- **Feedback Text Area:**
  - Placeholder: "What changes would you like? (required for Edit)"
  - Min height: 100px
  - Required when "Edit" is selected
  - Character count

- **Feedback History:**
  - Collapsible section
  - Shows previous feedback rounds
  - Helps user track what they've asked for

**Styling:**
```css
.review-section {
  background: white;
  border-radius: 12px;
  padding: var(--space-6);
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  border: 1px solid var(--gray-200);
}

.action-buttons {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: var(--space-3);
  margin-bottom: var(--space-6);
}

.button {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-2);
  padding: var(--space-3) var(--space-4);
  border-radius: 8px;
  font-size: var(--text-base);
  font-weight: var(--font-medium);
  border: 2px solid transparent;
  cursor: pointer;
  transition: all 0.2s;
}

.button-approve {
  background: var(--success-500);
  color: white;
  border-color: var(--success-600);
}

.button-approve:hover {
  background: var(--success-600);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(34, 197, 94, 0.3);
}

.button-edit {
  background: var(--primary-500);
  color: white;
  border-color: var(--primary-600);
}

.button-edit:hover {
  background: var(--primary-600);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3);
}

.button-regenerate {
  background: var(--warning-500);
  color: white;
  border-color: var(--warning-600);
}

.button-regenerate:hover {
  background: var(--warning-600);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(245, 158, 11, 0.3);
}

.button-reject {
  background: var(--error-500);
  color: white;
  border-color: var(--error-600);
}

.button-reject:hover {
  background: var(--error-600);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(239, 68, 68, 0.3);
}

.feedback-textarea {
  width: 100%;
  min-height: 100px;
  padding: var(--space-4);
  border: 2px solid var(--gray-200);
  border-radius: 8px;
  font-family: var(--font-sans);
  font-size: var(--text-base);
  line-height: 1.6;
  resize: vertical;
  transition: border-color 0.2s, box-shadow 0.2s;
}

.feedback-textarea:focus {
  border-color: var(--primary-500);
  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
  outline: none;
}

.feedback-history {
  margin-top: var(--space-4);
  padding: var(--space-4);
  background: var(--gray-50);
  border-radius: 8px;
  border: 1px solid var(--gray-200);
}

.feedback-item {
  padding: var(--space-2) 0;
  border-bottom: 1px solid var(--gray-200);
}

.feedback-item:last-child {
  border-bottom: none;
}

.feedback-round {
  font-size: var(--text-sm);
  color: var(--gray-500);
  margin-bottom: var(--space-1);
}

.feedback-text {
  color: var(--gray-700);
}
```

---

### 7. Final Letter Display (Step 6)

**Purpose:** Show the finalized cover letter with salutation and sign-off

**Components:**
- **Header:** "Your Final Cover Letter"
- **Success Badge:** "Approved & Saved"
- **Letter Display:**
  - Full letter with salutation and sign-off
  - Formatted with proper spacing
  - Copy button (top right)
  - Download button (top right)
- **Metadata:**
  - Company name
  - Role title
  - Date generated
  - Revision count
  - Model used
- **Next Steps:**
  - "Generate Another" button
  - "View Application History" link

**Styling:**
```css
.final-letter-container {
  background: white;
  border-radius: 12px;
  padding: var(--space-8);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  border: 2px solid var(--success-200);
}

.success-badge {
  display: inline-flex;
  align-items: center;
  gap: var(--space-2);
  background: var(--success-100);
  color: var(--success-700);
  padding: var(--space-2) var(--space-4);
  border-radius: 9999px;
  font-size: var(--text-sm);
  font-weight: var(--font-medium);
  margin-bottom: var(--space-4);
}

.letter-content {
  font-family: var(--font-sans);
  font-size: var(--text-base);
  line-height: 1.8;
  color: var(--gray-800);
  white-space: pre-wrap;
  padding: var(--space-6);
  background: var(--gray-50);
  border-radius: 8px;
  border: 1px solid var(--gray-200);
}

.metadata-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: var(--space-4);
  margin-top: var(--space-6);
  padding: var(--space-4);
  background: var(--gray-50);
  border-radius: 8px;
}

.metadata-item {
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
}

.metadata-label {
  font-size: var(--text-sm);
  color: var(--gray-500);
  font-weight: var(--font-medium);
}

.metadata-value {
  font-size: var(--text-base);
  color: var(--gray-800);
}

.action-buttons {
  display: flex;
  gap: var(--space-3);
  margin-top: var(--space-6);
}

.button-secondary {
  background: white;
  color: var(--gray-700);
  border: 2px solid var(--gray-300);
  padding: var(--space-3) var(--space-6);
  border-radius: 8px;
  font-size: var(--text-base);
  font-weight: var(--font-medium);
  cursor: pointer;
  transition: all 0.2s;
}

.button-secondary:hover {
  background: var(--gray-50);
  border-color: var(--gray-400);
  transform: translateY(-1px);
}
```

---

### 8. Application History Sidebar

**Purpose:** Show past applications and allow quick access

**Components:**
- **Header:** "Application History"
- **List Items:**
  - Company name (bold)
  - Role title
  - Date
  - Status badge (Approved/Rejected)
  - Click to expand and view letter
- **Empty State:**
  - Message: "No applications yet"
  - Icon: Document (📄)
- **Filter/Sort:**
  - Filter by status
  - Sort by date (newest first)

**Styling:**
```css
.history-section {
  margin-top: var(--space-6);
  padding-top: var(--space-6);
  border-top: 1px solid var(--gray-200);
}

.history-item {
  padding: var(--space-3);
  border-radius: 8px;
  margin-bottom: var(--space-2);
  cursor: pointer;
  transition: background 0.2s;
  border: 1px solid transparent;
}

.history-item:hover {
  background: var(--gray-100);
  border-color: var(--gray-200);
}

.history-company {
  font-weight: var(--font-semibold);
  color: var(--gray-800);
  margin-bottom: var(--space-1);
}

.history-role {
  font-size: var(--text-sm);
  color: var(--gray-600);
  margin-bottom: var(--space-1);
}

.history-date {
  font-size: var(--text-xs);
  color: var(--gray-400);
}

.history-status {
  display: inline-block;
  padding: var(--space-1) var(--space-2);
  border-radius: 4px;
  font-size: var(--text-xs);
  font-weight: var(--font-medium);
}

.history-status.approved {
  background: var(--success-100);
  color: var(--success-700);
}

.history-status.rejected {
  background: var(--error-100);
  color: var(--error-700);
}
```

---

### 9. Footer

**Purpose:** Status information, version, links

**Components:**
- **Status:** "Connected" / "Disconnected"
- **Version:** "v0.1.0"
- **Links:** GitHub, Documentation, Feedback
- **Copyright:** "© 2025 DRAFTRON"

**Styling:**
```css
.footer {
  background: white;
  border-top: 1px solid var(--gray-200);
  padding: var(--space-4) var(--space-6);
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: var(--text-sm);
  color: var(--gray-500);
}

.footer-status {
  display: flex;
  align-items: center;
  gap: var(--space-2);
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--success-500);
}

.status-dot.disconnected {
  background: var(--error-500);
}

.footer-links {
  display: flex;
  gap: var(--space-4);
}

.footer-link {
  color: var(--gray-500);
  text-decoration: none;
  transition: color 0.2s;
}

.footer-link:hover {
  color: var(--primary-500);
}
```

---

## State Management

### Session State Variables
```python
# Core state
st.session_state.thread_id        # Unique ID for this session
st.session_state.result           # Current graph result
st.session_state.current_step     # Current pipeline step
st.session_state.is_processing    # Whether AI is working

# UI state
st.session_state.show_critique    # Whether critique section is expanded
st.session_state.show_history     # Whether history sidebar is visible
st.session_state.feedback_text    # Current feedback text

# History
st.session_state.applications     # List of past applications
```

### State Transitions
```
INITIAL → INPUT → PROCESSING → REVIEW → FINALIZED
                                    ↓
                                  EDITING → PROCESSING → REVIEW
                                    ↓
                                  REJECTED → INITIAL
```

---

## Responsive Design

### Breakpoints
```css
--breakpoint-sm: 640px;   /* Mobile landscape */
--breakpoint-md: 768px;   /* Tablet */
--breakpoint-lg: 1024px;  /* Desktop */
--breakpoint-xl: 1280px;  /* Large desktop */
```

### Mobile Adaptations
- **Sidebar:** Hidden by default, toggle button in header
- **Action Buttons:** Stack vertically instead of 2x2 grid
- **Draft Display:** Full width, smaller padding
- **Typography:** Slightly smaller headings

### Tablet Adaptations
- **Sidebar:** Collapsible, 240px width
- **Action Buttons:** 2x2 grid
- **Draft Display:** Full width with larger padding

---

## Accessibility

### Color Contrast
- All text meets WCAG AA standards (4.5:1 for normal text, 3:1 for large text)
- Interactive elements have visible focus states
- Error states use both color and icons

### Keyboard Navigation
- All interactive elements are focusable
- Tab order follows logical flow
- Escape key closes modals/collapsibles

### Screen Readers
- All images have alt text
- ARIA labels on interactive elements
- Live regions for dynamic content updates

### Motion
- Respect `prefers-reduced-motion`
- Disable animations when reduced motion is preferred

---

## Implementation Notes

### Streamlit-Specific Considerations

1. **Caching:**
   ```python
   @st.cache_resource
   def get_app():
       return DraftronGraph()
   ```

2. **Session State:**
   - Initialize all state variables on first load
   - Use `st.session_state.get()` with defaults

3. **Reruns:**
   - Streamlit reruns the entire script on every interaction
   - Use `st.cache_resource` for expensive operations
   - Store graph result in session state

4. **Components:**
   - Use `st.columns()` for layout
   - Use `st.expander()` for collapsible sections
   - Use `st.markdown()` with HTML for custom styling
   - Use `st.components.v1.html()` for complex custom components

5. **Styling:**
   - Inject custom CSS with `st.markdown("""<style>...</style>""", unsafe_allow_html=True)`
   - Use Streamlit's built-in themes when possible
   - Custom CSS for advanced styling

### File Structure
```
app.py                      # Main Streamlit app
├── components/
│   ├── header.py          # Header component
│   ├── sidebar.py         # Sidebar with pipeline & history
│   ├── input_section.py   # Job posting input
│   ├── draft_display.py   # Draft & critique display
│   ├── review_section.py  # Human review interface
│   ├── final_letter.py    # Final letter display
│   └── footer.py          # Footer component
├── styles/
│   └── main.css           # Custom CSS
└── utils/
    ├── state.py           # State management helpers
    └── formatting.py      # Text formatting utilities
```

### Performance Considerations
- Minimize API calls by caching graph instance
- Use `st.spinner()` for loading states
- Debounce text input to avoid excessive reruns
- Lazy load application history

---

## Color Usage Examples

### Success State
```python
st.success("✅ Cover letter approved and saved!")
```

### Warning State
```python
st.warning("⚠️ Self-critique flagged some issues. Review before approving.")
```

### Error State
```python
st.error("❌ Failed to generate cover letter. Please try again.")
```

### Info State
```python
st.info("💡 Tip: Include the full job description for better results.")
```

---

## Iconography

### Recommended Icons (Streamlit/Emoji)
- **Generate:** ✨ or 🪄
- **Approve:** ✅ or ✓
- **Edit:** ✏️
- **Regenerate:** 🔄
- **Reject:** ❌ or ✕
- **Download:** ⬇️
- **Copy:** 📋
- **History:** 📜
- **Settings:** ⚙️
- **Help:** ❓

---

## Animation Guidelines

### Transitions
- **Button hover:** 0.2s ease
- **Section expand/collapse:** 0.3s ease
- **Loading spinner:** 1s linear infinite
- **Success/error messages:** 0.5s ease-in

### Micro-interactions
- **Button press:** Scale down 0.98
- **Card hover:** Subtle shadow increase
- **Focus ring:** 0.1s ease-in

---

## Dark Mode (Future Enhancement)

### Dark Color Palette
```css
--dark-bg: #111827;
--dark-surface: #1f2937;
--dark-border: #374151;
--dark-text: #f9fafb;
--dark-text-secondary: #9ca3af;
```

### Implementation
- Use CSS custom properties
- Toggle with `st.toggle("Dark Mode")`
- Persist preference in session state

---

## Final Checklist

- [ ] Header with logo and title
- [ ] Sidebar with pipeline progress
- [ ] Job posting input with validation
- [ ] Loading states with spinners
- [ ] Draft display with formatting
- [ ] Critique section with badges
- [ ] Review interface with 4 action buttons
- [ ] Feedback text area
- [ ] Feedback history display
- [ ] Final letter with metadata
- [ ] Application history list
- [ ] Responsive design
- [ ] Accessibility compliance
- [ ] Error handling
- [ ] Loading performance

---

*This specification is a living document. Update as the project evolves.*
