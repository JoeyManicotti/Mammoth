# Workflow Tests for Mammoth Recommender Designer

This document provides step-by-step instructions for testing each of the 5 example workflows.

## Prerequisites

1. Navigate to http://localhost:3000/recommender-designer
2. Clear the canvas if there are existing components

## Test 1: Simple Collaborative Filtering

**Purpose:** Basic user-based recommendation system

**Components Needed:**
1. Data Source (Blue)
2. Train/Test Split (Purple)
3. Collaborative Filter (Amber)
4. Predictions (Green)
5. Evaluation (Green)

**Steps:**
1. Drag "Data Source" onto canvas (center-top)
2. Drag "Train/Test Split" below Data Source
3. Drag "Collaborative Filter" below Train/Test Split
4. Drag "Predictions" to the lower-left
5. Drag "Evaluation" to the lower-right

**Creating Connections:**
1. Click connection point on Data Source → click Train/Test Split
2. Click connection point on Train/Test Split → click Collaborative Filter
3. Click connection point on Collaborative Filter → click Predictions
4. Click connection point on Collaborative Filter → click Evaluation

**Expected Result:**
- All components connected in a flow
- Blue → Purple → Amber → Green branches
- Connection validation passes
- Save workflow using "💾 Save" button

## Test 2: XGBoost with Features

**Purpose:** Gradient boosting with user/item features

**Components Needed:**
1. Data Source (Blue)
2. Features (Blue)
3. Train/Test Split (Purple)
4. Preprocessor (Purple)
5. XGBoost (Amber)
6. Predictions (Green)
7. Evaluation (Green)

**Steps:**
1. Drag "Data Source" onto canvas (top-left)
2. Drag "Features" onto canvas (top-right)
3. Drag "Train/Test Split" below Data Source
4. Drag "Preprocessor" to the right of Train/Test Split
5. Drag "XGBoost" below and between them
6. Drag "Predictions" to lower-left
7. Drag "Evaluation" to lower-right

**Creating Connections:**
1. Data Source → Train/Test Split
2. Features → Preprocessor
3. Train/Test Split → XGBoost
4. Preprocessor → XGBoost
5. XGBoost → Predictions
6. XGBoost → Evaluation

**Expected Result:**
- Multiple inputs merge into XGBoost model
- Both data and features flow through preprocessing
- Output branches to Predictions and Evaluation
- More complex graph structure validates properly

## Test 3: Matrix Factorization Pipeline

**Purpose:** SVD-based collaborative filtering

**Components Needed:**
1. Data Source (Blue)
2. Train/Test Split (Purple)
3. Matrix Factorization (Amber)
4. Predictions (Green)
5. Evaluation (Green)

**Steps:**
1. Drag "Data Source" onto canvas
2. Drag "Train/Test Split" below it
3. Drag "Matrix Factorization" below Train/Test Split
4. Drag "Predictions" and "Evaluation" side-by-side below Matrix Factorization

**Creating Connections:**
1. Data Source → Train/Test Split
2. Train/Test Split → Matrix Factorization
3. Matrix Factorization → Predictions
4. Matrix Factorization → Evaluation

**Expected Result:**
- Linear flow with output branching
- Similar structure to Test 1 but with different model
- Validates SVD model configuration options when double-clicked

## Test 4: Deep Learning Pipeline

**Purpose:** Neural network with metadata features

**Components Needed:**
1. Data Source (Blue)
2. Features (Blue)
3. Train/Test Split (Purple)
4. Preprocessor (Purple)
5. Neural Network (Amber)
6. Predictions (Green)
7. Evaluation (Green)

**Steps:**
1. Drag "Data Source" onto canvas (top-left)
2. Drag "Features" onto canvas (top-right)
3. Drag "Train/Test Split" below Data Source
4. Drag "Preprocessor" below Features
5. Drag "Neural Network" in the center below both
6. Drag "Predictions" and "Evaluation" below Neural Network

**Creating Connections:**
1. Data Source → Train/Test Split
2. Features → Preprocessor
3. Train/Test Split → Neural Network
4. Preprocessor → Neural Network
5. Neural Network → Predictions
6. Neural Network → Evaluation

**Expected Result:**
- Dual-input pipeline merging into deep learning model
- Complex preprocessing and feature engineering flow
- Neural network configuration panel shows layer options

## Test 5: Model Comparison

**Purpose:** Compare multiple models on same data

**Components Needed:**
1. Data Source (Blue)
2. Train/Test Split (Purple)
3. XGBoost (Amber)
4. Random Forest (Amber)
5. Collaborative Filter (Amber)
6. Evaluation (Green)

**Steps:**
1. Drag "Data Source" onto canvas (top-center)
2. Drag "Train/Test Split" below it
3. Drag "XGBoost", "Random Forest", and "Collaborative Filter" side-by-side below Train/Test Split
4. Drag "Evaluation" at the bottom-center

**Creating Connections:**
1. Data Source → Train/Test Split
2. Train/Test Split → XGBoost
3. Train/Test Split → Random Forest
4. Train/Test Split → Collaborative Filter
5. XGBoost → Evaluation
6. Random Forest → Evaluation
7. Collaborative Filter → Evaluation

**Expected Result:**
- One-to-many split from Train/Test Split
- Three parallel model branches
- Many-to-one merge into Evaluation
- Tests complex connection validation

## General Testing Checklist

For each workflow, verify:

- [ ] All components drag and drop successfully
- [ ] Components show correct color gradient for their category
- [ ] Connection points are visible on hover/selection
- [ ] Connections can be created by clicking connection points
- [ ] Invalid connections are rejected
- [ ] Connection lines render with proper curves and arrows
- [ ] Connection delete button (×) works
- [ ] Components can be moved after placement
- [ ] Double-click opens configuration panel
- [ ] Right-click menu shows options
- [ ] Zoom in/out works properly
- [ ] Pan (Shift+Drag) works properly
- [ ] "💾 Save" downloads JSON file
- [ ] "📂 Load" can import the saved file
- [ ] Canvas persists when navigating away and back
- [ ] "❓ Help" opens help modal
- [ ] "🗑️ Clear Canvas" removes all components

## Connection Validation Tests

Test that these connections are **rejected**:
- Predictions → Data Source (backwards flow)
- Evaluation → Model (backwards flow)
- Model → Features (wrong direction)

Test that these connections are **accepted**:
- Data Source → Train/Test Split
- Train/Test Split → Any Model
- Preprocessor → Model
- Features → Preprocessor
- Model → Predictions
- Model → Evaluation

## Auto-save Testing

1. Create a workflow
2. Navigate to home page
3. Navigate back to /recommender-designer
4. Verify workflow is still there

## File Save/Load Testing

1. Create a complex workflow (e.g., Test 5)
2. Click "💾 Save" - should download JSON file
3. Clear canvas
4. Click "📂 Load" and select the downloaded file
5. Verify workflow is restored exactly

## Performance Testing

1. Add 20+ components to canvas
2. Verify smooth dragging
3. Verify zoom/pan still responsive
4. Create 30+ connections
5. Verify connection lines render smoothly

## Success Criteria

All workflows should:
1. Build without TypeScript errors ✓
2. Render with correct colors ✓
3. Allow valid connections ✓
4. Reject invalid connections ✓
5. Support configuration via double-click ✓
6. Save/load correctly ✓
7. Auto-save to localStorage ✓
8. Display help documentation ✓
