# Habit Tracker - Feature Specification

## Project Overview

A habit tracking application designed to help users create, monitor, and maintain habits with flexible tracking options and progress visualization.

### Technology Stack

- **Backend**: Flask (Python) with SQLAlchemy ORM
- **Frontend**: React (TypeScript) with Vite
- **Database**: MySQL 8.0
- **Deployment**: Dockerized stack with Docker Compose
- **Authentication**: JWT-based token authentication

---

## Core Features

### 1. User Management & Authentication

#### 1.1 User Registration
- [x] User signup with username and password
- [x] Password hashing (bcrypt)
- [x] Unique username validation
- [x] Return JWT token on successful registration

#### 1.2 Session Control
- [x] User login with credentials
- [x] JWT token generation (24-hour expiration)
- [x] Token verification endpoint
- [x] Frontend token storage (localStorage for "remember me", sessionStorage otherwise)
- [x] Automatic logout on token expiration (401 handling)
- [x] Protected routes requiring authentication

#### 1.3 User Interface
- [x] Login form component
- [x] Signup form component
- [x] "Remember me" checkbox for persistent sessions
- [x] Redirect to login for unauthenticated access

---

### 2. Habit Creation & Management

#### 2.1 Habit Types

**Value Types:**
- [x] **Boolean/Binary Habits**: Simple yes/no completion (target = 1)
  - Example: "Meditate today", "Read before bed"
- [x] **Quantitative Habits**: Numeric targets with units
  - Example: "Run 5 kilometers", "Practice 30 minutes", "Do 50 pushups"

**Success Criteria:**
- [x] **ABOVE Type**: Habit is successful when progress >= target
  - Example: "Run at least 5km" (success when value >= 5)
- [x] **BELOW Type**: Habit is successful when progress <= target (inverted)
  - Example: "Limit coffee to 2 cups" (success when value <= 2)

#### 2.2 Time Frames (Frequencies)
- [x] **Daily**: Progress tracked and reset each day
- [x] **Weekly**: Progress tracked and reset each week
- [x] **Monthly**: Progress tracked and reset each month
- [x] **Yearly**: Progress tracked and reset each year

#### 2.3 Habit Properties
- [x] Name (string, descriptive title)
- [x] Type (ABOVE or BELOW)
- [x] Frequency (DAILY, WEEKLY, MONTHLY, YEARLY)
- [x] Target value (numeric, can be 0 for BELOW habits)
- [x] Unit (string, e.g., "minutes", "km", "reps", "cups")
- [x] Start date (when habit tracking begins)
- [x] User association (foreign key)

#### 2.4 Habit CRUD Operations
- [x] Create new habit
  - [x] Validation: ABOVE habits require target > 0
  - [x] Default start_date to today if not specified
- [x] List all user's habits
- [x] Update/edit habit
- [x] Delete habit (with cascading progress entry deletion)

#### 2.5 Habit Management UI
- [x] Dashboard component displaying all habits
- [x] Habit cards showing name, type, frequency, and progress
- [x] Add Habit modal with form
- [x] Edit Habit modal with pre-filled values
- [x] Delete confirmation modal
- [x] Unit field input in Add/Edit modals
- [x] Quantitative checkbox (toggle between binary and quantitative habits)

---

### 3. Progress Tracking

#### 3.1 Progress Entry Creation
- [x] Record progress value for a habit
- [x] Associate progress with specific date
- [x] Default to current date if not specified
- [x] Support for numeric values (including decimals)
- [x] Validation: Prevent future-dated entries
- [x] Backend-driven completion status

#### 3.2 Progress Entry Management
- [x] Add progress via modal
- [x] Separate modals for binary (toggle) vs quantitative (numeric input)
- [x] Delete individual progress entries
- [x] Automatic date filtering based on habit frequency
- [x] Query progress by date range

#### 3.3 Progress Entry UI
- [x] "Mark Complete" modal for binary habits
- [x] "Add Progress" modal for quantitative habits
- [x] Display current progress value in habit card
- [x] Display units alongside progress values
- [x] Visual progress indicators
  - [x] Checkbox icons for binary habits (empty/checked)
  - [x] Progress bars for quantitative habits with percentage fill

---

### 4. Statistics & Streaks

#### 4.1 Streak Calculation
- [x] Current streak counter per habit
- [x] Context-aware calculation (respects habit frequency)
  - Daily habits: consecutive days
  - Weekly habits: consecutive weeks
  - Monthly habits: consecutive months
  - Yearly habits: consecutive years
- [x] Handles partial current period (doesn't break streak if period incomplete)
- [x] Detects streak breaks (missing periods)
- [x] Start date awareness (streak can't begin before habit creation)

#### 4.2 Statistics Display
- [x] Streak badge on habit cards
- [x] Stats API endpoint returning all habit streaks
- [ ] **Missing**: Percentage of completed periods
  - Calculate: (successful periods / total periods since start_date) * 100
  - Example: "Completed 15/20 days (75%)" or "12/16 weeks (75%)"
- [ ] **Missing**: Stats view/page
- [ ] **Missing**: Historical trends and graphs
- [ ] **Missing**: Best streak (longest ever)

---

## Implementation Status Summary

### Fully Implemented
- User authentication (signup, login, JWT)
- Habit CRUD operations
- Progress entry creation and deletion
- Streak calculation logic
- Modal-based UI workflow
- Docker containerization
- Database migrations
- Test coverage for core features
- Unit field (input, storage, display)

### Partially Implemented
- Progress filtering (backend supports it, frontend uses defaults)

### Not Implemented
- **Stats view**: Percentage completion rates
- **Server-side error display**: Show API validation errors in UI
- **Historical analytics**: Graphs, trends, best streaks

---

## Data Models

### User
```python
{
  id: Integer (PK)
  username: String (unique, indexed)
  password: LargeBinary (bcrypt hashed)
}
```

### Habit
```python
{
  id: Integer (PK)
  name: String
  type: Enum ['ABOVE', 'BELOW']
  frequency: Enum ['DAILY', 'WEEKLY', 'MONTHLY', 'YEARLY']
  target_value: Float (nullable, can be 0 for BELOW)
  unit: String (20 chars, nullable)
  start_date: Date
  user_id: Integer (FK -> User)
}
```

### ProgressEntry
```python
{
  id: Integer (PK)
  date: Date
  value: Float
  habit_id: Integer (FK -> Habit, cascade delete)
}
```

---

## API Endpoints

### Authentication (`/api/auth`)
- `POST /signup` - Create user account
- `POST /login` - Authenticate and receive token
- `GET /verify` - Validate current token

### Habits (`/api/habits`)
- `POST /` - Create new habit
- `GET /` - List user's habits
- `PATCH /{id}` - Update habit
- `DELETE /{id}` - Delete habit and associated progress

### Progress (`/api/progress`)
- `POST /` - Add progress entry
- `GET /` - Query progress entries (filterable by habit, date range)
- `DELETE /{id}` - Remove progress entry

### Stats (`/api/stats`)
- `GET /` - Get current streaks for all habits
- [ ] **TODO**: Add percentage completion endpoint

---

## Future Enhancements (Post-MVP)

### Advanced Features
- [ ] Habit categories/tags
- [ ] Multi-user support (teams, accountability partners)
- [ ] Habit templates/presets
- [ ] Reminders and notifications
- [ ] Data export (CSV, JSON)
- [ ] Dark mode

### Analytics
- [ ] Calendar heatmap view
- [ ] Trend analysis
- [ ] Comparative stats (this week vs last week)
- [ ] Habit correlation insights

### UX Improvements
- [ ] Enhanced visual distinction for ABOVE vs BELOW habits (icons, colors, clearer labels)
- [ ] Drag-and-drop habit reordering
- [ ] Bulk operations (mark multiple habits complete)
- [ ] Undo/redo functionality
- [ ] Keyboard shortcuts

---

## Technical Debt & Improvements

### Code Quality
- [ ] Consolidate similar modals (AddProgress + MarkComplete)
- [ ] Unify CSS button classes (.add-button, .save-button → .button-primary)
- [ ] Extract `getProgress()` calculation from HabitCard (memoize or backend)
- [ ] Move completion logic from frontend to backend
- [ ] Extract `get_habit_dict` as common pattern (backend/app/routes/stats.py:16)

### Testing
- [ ] Use pytest factories instead of fixtures
- [ ] Add parametrization for edge cases
- [ ] Mock nested helper function calls
- [ ] Frontend unit tests (currently none)
- [ ] E2E integration tests

### DevOps
- [ ] Runtime environment variable injection (replace build-time VITE_API_URL)
- [ ] CI/CD pipeline
- [ ] Production deployment configuration
- [ ] Database backups and migrations strategy

---

## Security Considerations

- [x] Password hashing with bcrypt
- [x] JWT token expiration (24 hours)
- [x] Token-based route protection
- [x] CORS configuration
- [ ] Rate limiting on authentication endpoints
- [ ] Password strength requirements
- [ ] Account lockout after failed attempts
- [ ] HTTPS enforcement in production

---

## Notes

### Design Decisions
1. **ABOVE/BELOW vs Binary/Quantitative**: The system uses ABOVE/BELOW to define success criteria rather than data types. A binary habit is simply `target=1` with ABOVE type.

2. **Period-based Progress**: Progress queries automatically filter to current period based on habit frequency, preventing confusion about "which week's progress am I seeing?"

3. **Streak Definition**: Streaks count consecutive successful periods. The current period doesn't break a streak if incomplete (allows users to still complete it).

4. **Cascading Deletes**: Deleting a habit removes all associated progress entries to maintain data integrity.

### Known Issues
- API validation errors not shown to users

---

## Version History

- **v0.1** (2025-04-24): Initial migration, core models
- **v0.2** (2025-05-18): User authentication added
- **v0.3** (2025-08-21): ABOVE/BELOW type system implemented
- **v0.4** (2025-08-23): Streak tracking with start_date
- **v0.5** (2025-08-28): Unit field added to Habit model
- **v0.6** (2026-01-04): Unit field fully integrated (UI input, API, display, tests)
- **v0.7** (2026-01-04): Quantitative checkbox toggle for habit creation/editing
- **v0.8** (2026-01-06): Future-dated progress entry validation with dynamic test
- **v0.9** (2026-01-07): Visual progress indicators (checkboxes for binary, progress bars for quantitative)
- **v1.0** (2026-01-08): Backend-driven completion status with comprehensive tests
- **Current**: Core functionality complete, analytics features pending
