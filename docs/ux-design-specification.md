# Airlock - UX Design Specification

**Author:** BMad (UX Designer Agent)
**Date:** 2025-11-12
**Version:** 1.0
**Project:** Airlock - Security-First Package Manager

---

## Executive Summary

This UX Design Specification provides comprehensive design guidance for the Airlock frontend application. The design emphasizes security-first principles, developer-friendly workflows, and WCAG 2.1 Level AA accessibility compliance. The specification uses the atomic design pattern for component organization and Material UI (MUI) as the foundation library.

**Design Philosophy:**
- **Security First:** Visual indicators reinforce security practices and build trust
- **Developer-Friendly:** Efficient workflows with minimal friction
- **Transparent:** Clear visibility into approval status and package usage
- **Accessible:** WCAG AA compliant, keyboard navigable, screen reader friendly
- **Professional:** Clean, modern interface that conveys reliability

---

## Design System Foundation

### Technology Stack

**UI Framework:** Material UI (MUI) - Latest from npm
- Provides accessibility features out-of-the-box
- Consistent design language
- Comprehensive component library
- Theme customization support

**Data Tables:** TanStack Material React Table (MRT) - Latest from npm
- Built on Material UI with TanStack Table
- Inline column filtering
- Global search
- Virtualization for performance
- Built-in pagination, sorting, row selection
- Column visibility toggles
- Export functionality
- Accessibility features built-in

**Component Architecture:** Atomic Design Pattern
- **Atoms:** Use Material UI components directly (Button, TextField, FormLabel, Icon, Badge, Typography, Card, etc.)
- **Molecules:** Custom components that compose MUI components (FormField, SearchBar, FileUpload)
- **Organisms:** Complex UI sections (Navigation, SubmissionForm, ApprovalForm)
- **Tables:** Use TanStack Material React Table (MRT) for all data tables - provides inline filtering, virtualization, pagination, sorting, and more
- **Templates:** Page layouts (DashboardLayout, FormLayout, AuthLayout)
- **Pages:** Full page components (HomePage, SubmissionPage, ApprovalPage)

**Test File Organization:**
- Component unit tests: `{ComponentName}.test.tsx` co-located with component
- Storybook stories: `{ComponentName}.stories.tsx` co-located with component
- Service mocks: `{ServiceName}.mock.ts` co-located with service
- All test files in same subfolder as the file they test

---

## Visual Design Language

### Color Palette

**Material UI Default Palette:**
- Use Material UI's default color palette without customization
- MUI provides semantic colors (primary, secondary, success, error, warning, info) that meet accessibility standards
- Status indicators should use MUI's semantic colors in combination with icons and text (never color alone)
- Ensure proper contrast ratios (MUI defaults meet WCAG AA standards)

**Semantic Color Usage:**
- Use color in combination with icons and text (never color alone)
- Status indicators: Badge with icon + color + text label
- Use MUI's semantic color variants (success, error, warning, info) for status
- Support high contrast mode (MUI handles this automatically)

### Typography

**Material UI Default Typography:**
- Use Material UI's default typography system without customization
- MUI default font family (Roboto) provides excellent readability
- Use MUI Typography component variants (h1-h6, body1, body2, caption) as-is
- For package names, versions, and code: Use MUI's Typography component with `fontFamily="monospace"` prop

**Typography Guidelines:**
- Clear hierarchy using MUI's default type scale
- Monospace fonts for package names, versions, IDs (via `fontFamily="monospace"`)
- Text resizable up to 200% without breaking layout (MUI handles this)
- Proper heading hierarchy (h1 → h2 → h3) for screen readers

### Spacing & Layout

**Spacing System (Material UI 8px grid):**
- **xs:** 4px - Tight spacing
- **sm:** 8px - Small gaps
- **md:** 16px - Default spacing
- **lg:** 24px - Section spacing
- **xl:** 32px - Large section spacing
- **xxl:** 48px - Page-level spacing

**Layout Principles:**
- Consistent margins and padding
- Responsive breakpoints (xs, sm, md, lg, xl)
- Maximum content width: 1200px for readability
- Card-based layout for content sections
- Clear visual hierarchy

### Icons

**Icon Library:** Material Icons (MUI)
- Consistent icon set throughout application
- Semantic icons for actions and status
- Icon + text labels for clarity (never icon alone)
- Accessible icon labels (aria-label)

**Common Icons:**
- **Security:** `Security`, `Verified`, `Lock`
- **Status:** `CheckCircle`, `Cancel`, `Pending`, `Warning`
- **Actions:** `Upload`, `Download`, `Search`, `Filter`, `Settings`
- **Navigation:** `Home`, `Dashboard`, `List`, `Person`

---

## Component Specifications (Atomic Design)

**Note:** Use Material UI components directly for basic building blocks (Button, TextField, FormLabel, Icon, Badge, Typography, Card, etc.). Only create custom components when composing multiple MUI components or adding custom functionality.

### Molecules

**FormField (`FormField.tsx`)**
- Composition: MUI FormLabel + MUI TextField + Error message
- States: default, error, disabled
- Accessibility: Label associated with input, error message announced
- Test: `FormField.test.tsx`, `FormField.stories.tsx`

**SearchBar (`SearchBar.tsx`)**
- Composition: MUI TextField + Search icon + Clear button
- Real-time search with debounce
- Accessibility: Search role, aria-label, keyboard accessible
- Test: `SearchBar.test.tsx`, `SearchBar.stories.tsx`

**FileUpload (`FileUpload.tsx`)**
- Composition: MUI TextField (file input) + MUI Button + File preview
- Drag-and-drop support
- File validation feedback
- Accessibility: Keyboard accessible, clear instructions
- Test: `FileUpload.test.tsx`, `FileUpload.stories.tsx`

**CheckResultCard (`CheckResultCard.tsx`)**
- Composition: MUI Card + MUI Typography + MUI Badge + Results + Timestamp
- Visual indicators for pass/fail
- Expandable for detailed results
- Accessibility: Status announced, keyboard expandable
- Test: `CheckResultCard.test.tsx`, `CheckResultCard.stories.tsx`

**PackageInfoCard (`PackageInfoCard.tsx`)**
- Composition: MUI Card + MUI Typography (monospace for package names) + Metadata
- Monospace font for package names (via Typography `fontFamily="monospace"`)
- Clear information hierarchy
- Accessibility: Proper heading structure
- Test: `PackageInfoCard.test.tsx`, `PackageInfoCard.stories.tsx`

### Organisms

**Note:** For data tables, use TanStack Material React Table (MRT) directly. It provides built-in features including inline filtering, column filtering, virtualization, pagination, sorting, row selection, and accessibility support.

**Navigation (`Navigation.tsx`)**
- Composition: MUI AppBar + MUI Drawer + MUI Menu items
- Role-based menu items
- Active route indication
- Accessibility: Skip navigation link, keyboard navigation, ARIA landmarks
- Test: `Navigation.test.tsx`, `Navigation.stories.tsx`

**SubmissionForm (`SubmissionForm.tsx`)**
- Composition: FileUpload + MUI Typography (project info) + Dependencies list + MUI Button
- Multi-step form with validation
- Progress indicators (MUI Stepper or LinearProgress)
- Accessibility: Form validation announced, keyboard navigation
- Test: `SubmissionForm.test.tsx`, `SubmissionForm.stories.tsx`

**ApprovalForm (`ApprovalForm.tsx`)**
- Composition: PackageInfoCard + CheckResultCard(s) + MUI Button (approve/reject) + MUI TextField (comment)
- Override functionality for failed checks
- Clear workflow status
- Accessibility: All actions keyboard accessible, status announced
- Test: `ApprovalForm.test.tsx`, `ApprovalForm.stories.tsx`

**WorkflowStatusDisplay (`WorkflowStatusDisplay.tsx`)**
- Composition: MUI Stepper + MUI Badge + Current stage indicator
- Visual workflow progression
- Stage descriptions
- Accessibility: Status announced, keyboard navigable timeline
- Test: `WorkflowStatusDisplay.test.tsx`, `WorkflowStatusDisplay.stories.tsx`

**FilterBar (`FilterBar.tsx`)**
- Composition: MUI Select + MUI Checkbox + MUI DatePicker + Reset button
- Clear filter indicators
- Reset functionality
- Accessibility: Keyboard accessible, filter state announced
- Test: `FilterBar.test.tsx`, `FilterBar.stories.tsx`

**Note on Tables:** All data tables use TanStack Material React Table (MRT) which provides:
- Inline column filtering
- Global search
- Virtualization for large datasets
- Built-in pagination
- Sorting and multi-column sorting
- Row selection
- Column visibility toggles
- Export functionality
- Accessibility features (ARIA roles, keyboard navigation)
- No need for custom DataTable or LicenseTable components - use MRT directly with column definitions

**LicenseForm (`LicenseForm.tsx`)**
- Composition: MUI TextField (identifier, name) + MUI Textarea (description) + MUI Switch (active) + MUI Button (save/cancel)
- Form validation for SPDX license identifiers
- Duplicate prevention
- Used in modal for add/edit operations
- Accessibility: Form accessibility, error messages associated
- Test: `LicenseForm.test.tsx`, `LicenseForm.stories.tsx`

### Templates

**DashboardLayout (`DashboardLayout.tsx`)**
- Composition: Navigation + Main content area + Sidebar (optional)
- Responsive layout
- Consistent header/footer
- Accessibility: Skip links, ARIA landmarks, keyboard navigation
- Test: `DashboardLayout.test.tsx`, `DashboardLayout.stories.tsx`

**FormLayout (`FormLayout.tsx`)**
- Composition: Header + Form content + Action buttons
- Centered form layout
- Progress indicators for multi-step forms
- Accessibility: Form structure, keyboard navigation
- Test: `FormLayout.test.tsx`, `FormLayout.stories.tsx`

**AuthLayout (`AuthLayout.tsx`)**
- Composition: Centered card + Logo + Form + Footer links
- Minimal, focused design
- Accessibility: Form structure, keyboard navigation
- Test: `AuthLayout.test.tsx`, `AuthLayout.stories.tsx`

### Pages

**HomePage (`HomePage.tsx`)**
- Composition: DashboardLayout + Welcome section + Quick actions + Recent activity
- Role-based content
- Quick links to common tasks
- Accessibility: Proper heading hierarchy, keyboard navigation
- Test: `HomePage.test.tsx`

**PackageSubmissionPage (`PackageSubmissionPage.tsx`)**
- Composition: FormLayout + SubmissionForm
- Clear instructions
- Validation feedback
- Success/error states
- Accessibility: Form accessibility, keyboard navigation
- Test: `PackageSubmissionPage.test.tsx`

**ApprovalWorkflowPage (`ApprovalWorkflowPage.tsx`)**
- Composition: DashboardLayout + Pending requests list + ApprovalForm
- Filterable pending requests
- Package details modal/sidebar
- Workflow status display
- Accessibility: Table accessibility, form accessibility, keyboard navigation
- Test: `ApprovalWorkflowPage.test.tsx`

**PackageTrackingPage (`PackageTrackingPage.tsx`)**
- Composition: DashboardLayout + TanStack Material React Table (MRT) + Usage charts
- MRT provides built-in search, filtering, pagination, sorting
- Package usage visualization
- Export functionality (via MRT)
- Accessibility: MRT handles table accessibility
- Test: `PackageTrackingPage.test.tsx`

**AdminConfigurationPage (`AdminConfigurationPage.tsx`)**
- Composition: DashboardLayout + Tab navigation + Configuration sections
- User management
- System configuration
- Audit log viewer
- Accessibility: Tab navigation, form accessibility
- Test: `AdminConfigurationPage.test.tsx`

**LicenseManagementPage (`LicenseManagementPage.tsx`)**
- Composition: DashboardLayout + TanStack Material React Table (MRT) + LicenseForm (modal)
- MRT provides built-in search, filtering, pagination, sorting for license table
- License allowlist management
- Add, edit, activate/deactivate licenses
- SPDX identifier validation
- Accessibility: MRT handles table accessibility, form accessibility, keyboard navigation
- Test: `LicenseManagementPage.test.tsx`

---

## Page Specifications

### 1. Home Page / Dashboard

**Purpose:** Central hub for users to access common tasks and view system status

**Layout:**
- Navigation bar (top)
- Welcome section with user role
- Quick action cards (role-based):
  - Submitter: "Submit Package Request", "View My Submissions"
  - Reviewer: "Review Pending Requests", "View Workflow Status"
  - Admin: "Manage Users", "System Configuration", "License Management", "View Audit Logs"
- Recent activity feed
- System statistics (if admin)

**Accessibility:**
- Skip navigation link
- Proper heading hierarchy (h1: Welcome, h2: Quick Actions, h2: Recent Activity)
- Keyboard navigation for all cards
- Screen reader announcements for dynamic content

### 2. Package Request Submission Page

**Purpose:** Allow submitters to upload package-lock.json files and create package requests

**Layout:**
- FormLayout template
- File upload area (drag-and-drop + file picker)
- Auto-extracted project information (read-only):
  - Project name (from package-lock.json root `name`)
  - Project version (from package-lock.json root `version`)
- Extracted dependencies list (read-only):
  - Package name + version pairs
  - Scrollable list if many dependencies
- Submit button
- Validation feedback (inline errors)
- Success state: Submission ID, link to view status

**User Flow:**
1. User navigates to submission page
2. User uploads package-lock.json file
3. System extracts and displays project name/version
4. System extracts and displays dependencies
5. User reviews extracted information
6. User clicks "Submit"
7. System validates and creates submission
8. Success message with submission ID

**Accessibility:**
- Form labels properly associated
- File upload keyboard accessible
- Error messages announced
- Success message announced
- Keyboard navigation throughout

### 3. Approval Workflow Page

**Purpose:** Allow reviewers to review package requests and make approval decisions

**Layout:**
- DashboardLayout template
- Left sidebar: Pending requests list (filterable)
- Main content: Selected package request details
  - Package request information (name, version, requesting project)
  - Package details (fetched from NPM): description, repository, maintainers
  - Workflow status display (timeline/stepper)
  - Automated check results:
    - Trivy scan results (vulnerabilities list)
    - License check results (license type, allowlist status)
    - Visual pass/fail indicators
  - Action buttons: Approve, Reject
  - Comment field (required for rejections, optional for approvals)
  - Override option (if checks failed):
    - Checkbox: "Override check failures"
    - Justification field (required if override selected)

**User Flow:**
1. Reviewer navigates to approval workflow page
2. Reviewer sees list of pending requests
3. Reviewer clicks on a request to view details
4. Reviewer reviews package information and check results
5. Reviewer makes decision:
   - If checks pass: Approve or Reject with comment
   - If checks fail: Override (with justification) or Reject
6. System processes decision and updates workflow
7. Success message, request removed from pending list

**Accessibility:**
- Table/list keyboard navigable
- All form fields keyboard accessible
- Status indicators announced
- Decision buttons clearly labeled
- Override option clearly explained

### 4. Package Tracking Dashboard

**Purpose:** View all approved packages, their usage, and status

**Layout:**
- DashboardLayout template
- Main content: TanStack Material React Table (MRT) with columns:
  - Package name (monospace)
  - Version
  - Registry
  - Status (approved, locked)
  - Usage count (number of projects using it)
  - Last updated
  - Actions (view details, request upgrade)
- Usage visualization (optional chart)
- MRT provides: global search, inline column filtering, pagination, sorting, export

**Features:**
- Global search (via MRT)
- Inline column filtering (via MRT)
- Multi-column sorting (via MRT)
- Pagination (via MRT)
- Row selection for bulk actions (via MRT)
- Export to CSV/JSON (via MRT)
- Virtualization for large datasets (via MRT)

**Accessibility:**
- MRT provides proper ARIA roles
- MRT handles keyboard navigation (arrow keys, tab)
- MRT provides screen reader support for table data
- MRT search and filter are keyboard accessible
- MRT export functionality is keyboard accessible

### 5. Admin Configuration Page

**Purpose:** System administration and configuration

**Layout:**
- DashboardLayout template
- Tab navigation:
  - **Users:** User management table (add, edit, delete, assign roles)
  - **Automated Checks:** Check configuration (enable/disable, configure thresholds)
  - **Storage/Registry:** Configure external storage and registry connections
  - **Audit Logs:** View system audit logs (filterable, searchable)
- Link to License Management page (separate page)

**Features:**
- Role-based access (admin only)
- Form validation
- Confirmation dialogs for destructive actions
- Audit trail for all changes

**Accessibility:**
- Tab navigation keyboard accessible
- All forms accessible
- Confirmation dialogs keyboard accessible
- Table accessibility for user management and audit logs

### 6. License Management Page

**Purpose:** Allow administrators to manage the license allowlist for package validation

**Layout:**
- DashboardLayout template
- Main content: TanStack Material React Table (MRT) with columns:
  - License identifier (SPDX format, monospace font)
  - License name (human-readable)
  - Description
  - Status (Active/Inactive badge)
  - Created by (user)
  - Created date
  - Updated date
  - Actions (edit, activate/deactivate)
- Add License button (opens modal/form)
- MRT provides: global search, inline column filtering (including status filter), pagination, sorting
- Edit License modal/form:
  - License identifier (SPDX format, validated)
  - License name
  - Description (optional, textarea)
  - Active status toggle
  - Save/Cancel buttons

**Features:**
- Global search by identifier or name (via MRT)
- Inline column filtering, including status filter (via MRT)
- Add new license with form validation
- Edit existing license
- Deactivate license (soft delete with confirmation dialog)
- Reactivate deactivated license
- SPDX identifier validation (client-side and server-side)
- Duplicate prevention
- Success/error toast notifications
- Pagination and sorting (via MRT)
- Virtualization for large license lists (via MRT)

**User Flow:**
1. Admin navigates to "License Management" (from Admin Configuration or navigation)
2. Admin sees list of all licenses in allowlist
3. Admin can:
   - Search for specific license
   - Filter by active/inactive status
   - Click "Add License" to add new license
   - Click "Edit" on existing license to modify
   - Click "Deactivate" to soft delete (with confirmation)
   - Click "Activate" on inactive license to reactivate
4. When adding/editing:
   - Admin fills in license identifier (SPDX format, e.g., "MIT", "Apache-2.0")
   - Admin fills in license name (human-readable)
   - Admin optionally adds description
   - Admin toggles active status
   - System validates SPDX identifier format
   - System prevents duplicate identifiers
   - Admin saves changes
5. Success message displayed, table refreshes

**Accessibility:**
- MRT provides proper ARIA roles for table
- MRT handles keyboard navigation (arrow keys, tab)
- MRT provides screen reader support for table data
- MRT search and filter are keyboard accessible
- Form fields properly labeled
- Error messages associated with inputs
- Confirmation dialogs keyboard accessible
- Status changes announced via aria-live regions

---

## User Flows & Interactions

### Flow 1: Developer Submits Package Request

**Steps:**
1. Developer navigates to "Submit Package Request" (Home page or navigation)
2. Developer uploads package-lock.json file
3. System extracts and displays:
   - Project name: `my-project`
   - Project version: `1.0.0`
   - Dependencies: List of package@version pairs
4. Developer reviews extracted information
5. Developer clicks "Submit"
6. System validates and creates submission
7. Success message: "Submission created: SUB-12345"
8. Developer can click "View Submission Status" to see package requests

**Design Considerations:**
- Clear file upload area with drag-and-drop
- Immediate feedback on file upload
- Clear display of extracted information
- Validation errors shown inline
- Success state with next steps

### Flow 2: Security Team Reviews Package Request

**Steps:**
1. Reviewer navigates to "Approval Workflow" page
2. Reviewer sees list of pending requests (sorted by date)
3. Reviewer clicks on a request
4. Reviewer views:
   - Package request: `lodash@4.17.21` requested by `my-project@1.0.0`
   - Package details: Description, repository, maintainers (from NPM)
   - Workflow status: "Automated Checks Complete"
   - Trivy scan: ✅ Pass (0 vulnerabilities)
   - License check: ✅ Pass (MIT - approved)
5. Reviewer reviews all information
6. Reviewer clicks "Approve" and adds optional comment
7. System processes approval
8. Success message, request removed from pending list

**Design Considerations:**
- Clear pending requests list
- Prominent display of check results
- Easy approve/reject actions
- Comment field for transparency
- Visual workflow status

### Flow 3: Developer Checks Package Status

**Steps:**
1. Developer navigates to "Package Tracking" dashboard
2. Developer searches for package name (e.g., "lodash")
3. Developer sees package in results:
   - `lodash@4.17.21` - Approved - Used by 5 projects
4. Developer clicks "View Details"
5. Developer sees:
   - Package information
   - Usage locations (list of projects)
   - Version lock status
   - Option to request upgrade

**Design Considerations:**
- Fast search functionality
- Clear status indicators
- Easy access to details
- Usage information visible

### Flow 4: Admin Manages System

**Steps:**
1. Admin navigates to "Admin Configuration"
2. Admin selects tab (e.g., "Users")
3. Admin views user management table
4. Admin adds/edits user or assigns role
5. Admin saves changes
6. System updates and logs audit event
7. Success message

**Design Considerations:**
- Clear tab navigation
- Intuitive forms
- Confirmation for destructive actions
- Audit trail visibility

### Flow 5: Admin Manages License Allowlist

**Steps:**
1. Admin navigates to "License Management" page
2. Admin sees list of all licenses in allowlist
3. Admin searches for "MIT" to find existing license
4. Admin clicks "Add License" to add new license
5. Admin fills in form:
   - License identifier: "BSD-2-Clause"
   - License name: "BSD 2-Clause License"
   - Description: "Simplified BSD License"
   - Active: Enabled
6. Admin clicks "Save"
7. System validates SPDX identifier and checks for duplicates
8. Success message: "License BSD-2-Clause added successfully"
9. Table refreshes showing new license
10. Admin can edit or deactivate licenses as needed

**Design Considerations:**
- Clear license table with search and filter
- Simple add/edit form with validation
- SPDX identifier format validation with helpful error messages
- Confirmation dialog for deactivation
- Immediate feedback on all actions
- Clear status indicators (active/inactive)

---

## Accessibility Requirements

### WCAG 2.1 Level AA Compliance

**Perceivable:**
- Text alternatives for all non-text content (images, icons)
- Captions for multimedia (if any)
- Sufficient color contrast (4.5:1 for normal text, 3:1 for large text)
- Text resizable up to 200% without loss of functionality
- Color not used as sole indicator (use icons + text)

**Operable:**
- Keyboard accessible for all functionality
- No keyboard traps
- Sufficient time (no time limits on forms)
- Navigable (skip links, headings, focus order)
- Input modalities (pointer gestures have keyboard alternatives)

**Understandable:**
- Readable (language identified)
- Predictable (consistent navigation, no unexpected changes)
- Input assistance (labels, error messages, suggestions)

**Robust:**
- Compatible (valid HTML, proper ARIA usage)
- Screen reader support
- Assistive technology compatible

### Keyboard Navigation

**Standard Navigation:**
- `Tab`: Move forward through interactive elements
- `Shift+Tab`: Move backward
- `Enter/Space`: Activate buttons, links
- `Arrow keys`: Navigate lists, tables, menus
- `Escape`: Close modals, dialogs
- `Home/End`: Jump to start/end of lists

**Custom Shortcuts:**
- `/`: Focus search bar
- `?`: Show keyboard shortcuts help

### Screen Reader Support

**ARIA Labels:**
- All interactive elements have descriptive labels
- Status changes announced via aria-live regions
- Form errors associated with inputs
- Table headers properly associated

**Semantic HTML:**
- Proper heading hierarchy (h1-h6)
- Lists for list content
- Tables for tabular data
- Forms with proper structure

**Live Regions:**
- Workflow status changes
- Form submission results
- Search results updates
- Error messages

### Focus Management

**Focus Indicators:**
- Visible focus outline (2px minimum, high contrast)
- Focus visible on all interactive elements
- Focus order follows logical flow

**Focus Trapping:**
- Modals trap focus within
- Escape key closes modals
- Focus returns to trigger after modal close

### High Contrast Mode

**Support:**
- All content readable in high contrast mode
- Status indicators use patterns/icons in addition to color
- Text maintains contrast ratios

---

## Responsive Design

### Breakpoints (Material UI)

- **xs:** 0px - Mobile phones
- **sm:** 600px - Tablets (portrait)
- **md:** 900px - Tablets (landscape), small laptops
- **lg:** 1200px - Desktops
- **xl:** 1536px - Large desktops

### Responsive Strategies

**Mobile (xs, sm):**
- Single column layout
- Collapsible navigation drawer
- Stacked form fields
- Full-width buttons
- Simplified tables (cards instead)
- Touch-friendly targets (44x44px minimum)

**Tablet (md):**
- Two-column layout where appropriate
- Side navigation drawer
- Standard form layouts
- Responsive tables

**Desktop (lg, xl):**
- Multi-column layouts
- Persistent side navigation
- Full feature set
- Maximum content width: 1200px

### Touch Targets

- Minimum size: 44x44px
- Adequate spacing between targets
- Large hit areas for important actions

---

## Error Handling & Feedback

### Error States

**Form Validation:**
- Inline error messages below fields
- Error icons next to invalid fields
- Summary of errors at top of form
- Error messages announced to screen readers

**API Errors:**
- User-friendly error messages
- Retry options where appropriate
- Clear error state in UI
- Error logging for debugging

**Empty States:**
- Helpful messages for empty lists
- Guidance on next steps
- Illustrations/icons for clarity

### Success States

**Form Submission:**
- Success message with next steps
- Confirmation of action taken
- Clear indication of what happened

**Status Updates:**
- Toast notifications for status changes
- Visual indicators (badges, icons)
- Status announced to screen readers

### Loading States

**Data Fetching:**
- Skeleton loaders for content
- Progress indicators for long operations
- Disabled states during loading
- Loading announced to screen readers

---

## Testing & Quality Assurance

### Component Testing (Storybook)

**Atomic Components:**
- Test atoms in isolation
- Test all states (default, hover, active, disabled, error)
- Test accessibility (keyboard, screen reader)
- Visual regression testing

**BDD Scenarios:**
- Gherkin scenarios for component behavior
- Storybook stories with BDD scenarios
- Test user interactions

### Accessibility Testing

**Automated:**
- axe-core integration in Storybook
- Pa11y for linting
- Lighthouse CI for audits
- Target: 100% WCAG AA compliance

**Manual:**
- Keyboard navigation testing
- Screen reader testing (NVDA, JAWS, VoiceOver)
- High contrast mode testing
- Zoom testing (50% to 200%)

### E2E Testing

**Critical Flows:**
- Package submission flow
- Approval workflow
- Package tracking
- Admin configuration

**BDD Framework:**
- Cucumber.js for Gherkin scenarios
- Playwright/Cypress for browser automation
- Test coverage for all user flows

---

## Implementation Guidelines

### Component Development

**Atomic Design Pattern:**
1. Use MUI components directly (no custom atoms needed)
2. Compose molecules from MUI components
3. Build organisms from molecules
4. Use TanStack Material React Table (MRT) directly for all data tables (no custom table components)
5. Create templates from organisms
6. Assemble pages from templates

**Data Tables:**
- Use TanStack Material React Table (MRT) directly in pages
- Define column configurations for each table
- MRT handles: filtering, sorting, pagination, virtualization, export, accessibility
- No need to create custom DataTable or table wrapper components
- Example: `PackageTrackingPage.tsx` uses MRT with package column definitions

**Co-located Files:**
- Component: `FormField.tsx`
- Test: `FormField.test.tsx`
- Storybook: `FormField.stories.tsx`
- All in same directory: `src/components/molecules/FormField/`

### State Management

**Global State (Zustand):**
- User authentication state
- UI preferences (theme, sidebar state)
- Global notifications

**Server State (React Query):**
- Package data
- Submission data
- Workflow data
- All API-fetched data

**Local State (React useState):**
- Form state
- UI component state
- Temporary selections

### Form Handling

**React Hook Form:**
- Form validation
- Error handling
- Performance optimization
- Accessibility support

**Validation:**
- Client-side validation with clear messages
- Server-side validation error display
- Real-time validation feedback

### API Integration

**Axios:**
- Centralized API client
- Request/response interceptors
- Error handling
- Token management

**React Query:**
- Data fetching
- Caching
- Refetching
- Optimistic updates

### Routing

**TanStack Router:**
- Type-safe routes
- Protected routes (role-based)
- Route parameters
- Query parameters

---

## Design Tokens & Theme

### Material UI Theme

**Default Theme:**
- Use Material UI's default theme without color or typography customization
- Inherit all colors and typography from MUI defaults
- Only customize layout-related properties if needed

**Layout Customizations (Optional):**
- Maximum content width: 1200px for readability (apply via container components)
- Consistent spacing using MUI's spacing system (8px grid)
- Card-based layout for content sections
- Custom layout templates (DashboardLayout, FormLayout, AuthLayout)

**Component Usage:**
- Use MUI components as-is with default styling
- Apply custom layout through composition and spacing
- Ensure accessibility through proper component usage (MUI handles this)

---

## Design Deliverables

### 1. Component Library (Storybook)
- All atomic components documented
- Interactive component playground
- BDD scenarios for components
- Accessibility testing integrated

### 2. Design System Documentation
- This specification document
- Component usage guidelines
- Accessibility guidelines
- Responsive design patterns

### 3. Visual Design Assets
- Icon library reference (Material Icons)
- Spacing system (MUI 8px grid)
- Layout specifications

### 4. Prototypes (Optional)
- High-fidelity mockups for key pages
- Interactive prototypes for user flows
- Design review materials

---

## Next Steps

1. **Component Development:**
   - Use MUI components directly for basic building blocks
   - Build custom molecules that compose MUI components
   - Build organisms from molecules
   - Test each custom component in Storybook

2. **Page Implementation:**
   - Implement templates (DashboardLayout, FormLayout, AuthLayout)
   - Build pages using templates and organisms
   - Test user flows end-to-end

3. **Accessibility Validation:**
   - Run automated accessibility tests
   - Perform manual testing with screen readers
   - Fix any accessibility issues

4. **User Testing (Optional):**
   - Conduct usability testing with target users
   - Gather feedback on workflows
   - Iterate based on feedback

---

## References

- **PRD:** `docs/PRD.md` - Product requirements and UX principles
- **Epics:** `docs/epics.md` - Frontend stories and component specifications
- **Architecture:** `docs/architecture.md` - Technical architecture and technology stack
- **Material UI Documentation:** https://mui.com/
- **WCAG 2.1 Guidelines:** https://www.w3.org/WAI/WCAG21/quickref/
- **Atomic Design Methodology:** https://atomicdesign.bradfrost.com/

---

_This UX Design Specification provides comprehensive guidance for implementing the Airlock frontend application with a focus on security, accessibility, and developer experience._

