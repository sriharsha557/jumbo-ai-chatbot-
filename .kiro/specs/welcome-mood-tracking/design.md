# Design Document - Welcome Page with Mood Tracking

## Overview

The Welcome Page serves as an intermediate screen between user authentication and the main chat interface, providing a personalized entry point with mood tracking capabilities. This design integrates seamlessly with the existing Jumbo AI application architecture while introducing new mood tracking functionality that enhances the user experience and provides valuable emotional context for conversations.

## Architecture

### Component Structure
```
WelcomePage.jsx
├── PersonalGreeting (Header Section)
├── MoodSelector (Interactive Component)
├── MoodTrend (Optional Visualization)
├── InspirationalMessage (Content Component)
└── NavigationCTA (Action Component)
```

### Data Flow
1. **Authentication State** → Welcome Page receives authenticated user data
2. **Mood Selection** → Captures user's current emotional state
3. **Data Storage** → Persists mood data to user profile/localStorage
4. **Navigation** → Passes mood context to Chat Interface
5. **Trend Analysis** → Retrieves historical mood data for visualization

### Integration Points
- **App.js**: Navigation routing between auth, welcome, and chat pages
- **Supabase**: User authentication and mood data persistence
- **ChatPage**: Receives mood context for enhanced conversations
- **API Backend**: Mood data storage and retrieval endpoints

## Components and Interfaces

### WelcomePage Component

**Props Interface:**
```typescript
interface WelcomePageProps {
  currentUser: {
    id: string;
    name: string;
    email: string;
    access_token?: string;
  };
  onContinueToChat: (moodData?: MoodEntry) => void;
}
```

**State Management:**
```typescript
interface WelcomePageState {
  selectedMood: MoodType | null;
  inspirationalMessage: string;
  moodHistory: MoodEntry[];
  isLoading: boolean;
  error: string | null;
}
```

### MoodSelector Component

**Mood Types:**
```typescript
type MoodType = 'very_happy' | 'happy' | 'neutral' | 'sad' | 'very_sad';

interface MoodOption {
  type: MoodType;
  emoji: string;
  label: string;
  color: string;
}
```

**Mood Options Configuration:**
- 😢 Very Sad (Red: #ef4444)
- 🙁 Sad (Orange: #f97316) 
- 😐 Neutral (Yellow: #eab308)
- 🙂 Happy (Light Green: #84cc16)
- 😀 Very Happy (Green: #10b981)

### InspirationalMessage Component

**Message Pool (20 Messages):**
```typescript
const INSPIRATIONAL_MESSAGES = [
  "You've got this. One small step at a time.",
  "Your feelings are valid, always.",
  "Breathe in calm, breathe out doubt.",
  "It's okay not to be okay.",
  "You've made progress simply by showing up today.",
  "Every sunrise brings another chance.",
  "You're stronger than you think.",
  "Small joys build big strength.",
  "Healing is a process, not a race.",
  "Today's a new page — write it with kindness.",
  "Your journey matters, and so do you.",
  "Progress isn't always visible, but it's always happening.",
  "Be gentle with yourself today.",
  "You have survived 100% of your difficult days so far.",
  "This moment is temporary, your strength is permanent.",
  "You are worthy of love and support.",
  "Every feeling you have is teaching you something.",
  "Your courage to continue is inspiring.",
  "You don't have to be perfect to be amazing.",
  "Tomorrow is a fresh start waiting for you."
];
```

## Data Models

### MoodEntry Model
```typescript
interface MoodEntry {
  id: string;
  user_id: string;
  mood_type: MoodType;
  timestamp: Date;
  session_id?: string;
  notes?: string;
}
```

### User Profile Extension
```typescript
interface UserProfile {
  // Existing fields...
  mood_history: MoodEntry[];
  last_mood_check: Date | null;
  mood_tracking_enabled: boolean;
}
```

### API Endpoints

**POST /api/v1/mood/entry**
```typescript
Request: {
  mood_type: MoodType;
  timestamp: string;
  notes?: string;
}
Response: {
  success: boolean;
  mood_entry: MoodEntry;
  message: string;
}
```

**GET /api/v1/mood/history**
```typescript
Query Parameters: {
  days?: number; // Default: 7
  limit?: number; // Default: 50
}
Response: {
  success: boolean;
  mood_history: MoodEntry[];
  trend_summary: {
    average_mood: number;
    mood_distribution: Record<MoodType, number>;
  };
}
```

## User Interface Design

### Layout Structure
```
┌─────────────────────────────────────┐
│           Personal Greeting          │
│        Hey [Name]! 🌼 How are       │
│         you feeling today?          │
├─────────────────────────────────────┤
│              Mood Selector          │
│    😢  🙁  😐  🙂  😀             │
│  Tap the emoji that best describes  │
│      how you feel right now         │
├─────────────────────────────────────┤
│          Mood Trend (Optional)      │
│     [Simple 7-day visualization]    │
├─────────────────────────────────────┤
│        Inspirational Message        │
│    "You've got this. One small      │
│        step at a time."             │
├─────────────────────────────────────┤
│           Navigation CTA            │
│        [Continue to Chat]           │
│   Jumbo is here to listen and      │
│          support you.               │
└─────────────────────────────────────┘
```

### Visual Design System

**Color Palette:**
- Background: Gradient matching existing GradientBackground component
- Primary Actions: Purple gradient (#8b5cf6 to #a855f7)
- Mood Colors: Emotional spectrum from red to green
- Text: White with opacity variations for hierarchy

**Typography:**
- Headers: Briskey font family (matching existing pattern)
- Body Text: Comfortaa font family (matching existing pattern)
- Sizes: Responsive scaling following existing component patterns

**Spacing & Layout:**
- Container: Max-width 672px (matching ChatPage)
- Sections: 32px vertical spacing
- Interactive Elements: 24px padding, 16px border radius
- Mobile: Responsive breakpoints at 768px and 480px

### Responsive Design

**Desktop (>768px):**
- Full layout with all sections visible
- Mood selector: Horizontal layout with larger touch targets
- Trend visualization: Full chart display

**Tablet (768px):**
- Maintained layout with adjusted spacing
- Mood selector: Slightly smaller but still horizontal
- Trend visualization: Simplified chart

**Mobile (<480px):**
- Stacked layout with increased touch targets
- Mood selector: Larger emojis for easier selection
- Trend visualization: Minimal or hidden for v1

## Error Handling

### Mood Selection Errors
- **Network Failure**: Store mood locally, sync when connection restored
- **API Timeout**: Show retry option, allow continuation without mood data
- **Invalid Selection**: Provide clear feedback and reset selector

### Data Persistence Errors
- **Storage Failure**: Graceful degradation with localStorage fallback
- **Sync Issues**: Queue mood entries for later synchronization
- **Authentication Errors**: Redirect to login with preserved mood data

### User Experience Errors
- **Loading States**: Skeleton screens and loading indicators
- **Empty States**: Encouraging messages for first-time users
- **Offline Mode**: Cached inspirational messages and local storage

## Testing Strategy

### Unit Testing
- **MoodSelector Component**: Emoji selection, state management, accessibility
- **InspirationalMessage Component**: Random selection, message display
- **Data Models**: Mood entry validation, timestamp handling
- **API Integration**: Request/response handling, error scenarios

### Integration Testing
- **Navigation Flow**: Landing → Auth → Welcome → Chat progression
- **Data Persistence**: Mood storage and retrieval across sessions
- **User Authentication**: Supabase integration with mood data
- **Responsive Design**: Cross-device layout and interaction testing

### User Experience Testing
- **Accessibility**: Screen reader compatibility, keyboard navigation
- **Performance**: Component loading times, animation smoothness
- **Cross-browser**: Compatibility across modern browsers
- **Mobile Usability**: Touch target sizes, gesture interactions

## Implementation Considerations

### Performance Optimization
- **Lazy Loading**: Load mood history only when trend component is visible
- **Caching**: Cache inspirational messages and recent mood data
- **Debouncing**: Prevent rapid mood selection changes
- **Image Optimization**: Use optimized emoji assets or system emojis

### Accessibility Features
- **ARIA Labels**: Comprehensive labeling for mood selection
- **Keyboard Navigation**: Full keyboard accessibility for all interactions
- **Screen Reader Support**: Descriptive text for mood states and trends
- **High Contrast**: Ensure mood colors meet accessibility standards

### Security & Privacy
- **Data Encryption**: Encrypt mood data in transit and at rest
- **User Consent**: Clear privacy notice for mood tracking
- **Data Retention**: Configurable retention periods for mood history
- **Anonymous Analytics**: Aggregate mood trends without personal identification

### Future Enhancements
- **Advanced Mood Tracking**: Granular mood scales, custom emotions
- **Mood Insights**: AI-powered mood pattern analysis
- **Integration with Chat**: Mood-aware conversation starters
- **Sharing Features**: Optional mood sharing with trusted contacts
- **Wellness Recommendations**: Personalized suggestions based on mood patterns