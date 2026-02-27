#!/bin/bash

PRESET=$1

SETTINGS="opencode/big-pickle"

if [ "$PRESET" = "quality" ]; then
 PLANNER="google/gemini-3.1-pro-preview"
 PLAN_CHECKER="google/gemini-3.1-pro-preview"
 RESEARCHER="google/gemini-3.1-pro-preview"
 RESEARCH_SYNTHESIZER="google/gemini-3.1-pro-preview"
 CODEBASE_MAPPER="google/gemini-3.1-pro-preview"
 EXECUTOR="google/antigravity-gemini-3-flash"
 DEBUGGER="google/antigravity-gemini-3-flash"
 VALIDATOR="google/gemini-3.1-pro-preview"
elif [ "$PRESET" = "quality-mix" ]; then
 PLANNER="google/gemini-3.1-pro-preview"
 PLAN_CHECKER="google/antigravity-gemini-3-flash"
 RESEARCHER="google/antigravity-gemini-3-flash"
 RESEARCH_SYNTHESIZER="google/gemini-3.1-pro-preview"
 CODEBASE_MAPPER="google/gemini-3.1-pro-preview"
 EXECUTOR="google/antigravity-gemini-3-flash"
 DEBUGGER="google/antigravity-gemini-3-flash"
 VALIDATOR="google/antigravity-gemini-3-flash"
elif [ "$PRESET" = "quality-claude" ]; then
 PLANNER="google/antigravity-claude-opus-4-5-thinking"
 PLAN_CHECKER="google/antigravity-claude-sonnet-4-5-thinking"
 RESEARCHER="google/antigravity-claude-sonnet-4-5-thinking"
 RESEARCH_SYNTHESIZER="google/antigravity-claude-sonnet-4-5-thinking"
 CODEBASE_MAPPER="google/antigravity-claude-opus-4-5-thinking"
 EXECUTOR="google/antigravity-claude-opus-4-5-thinking"
 DEBUGGER="google/antigravity-claude-opus-4-5-thinking"
 VALIDATOR="google/antigravity-claude-opus-4-5-thinking"
elif [ "$PRESET" = "quality-claude-mix" ]; then
 PLANNER="google/antigravity-claude-opus-4-5-thinking"
 PLAN_CHECKER="google/antigravity-claude-sonnet-4-5-thinking"
 RESEARCHER="google/antigravity-claude-sonnet-4-5-thinking"
 RESEARCH_SYNTHESIZER="google/antigravity-claude-opus-4-5-thinking"
 CODEBASE_MAPPER="google/antigravity-claude-opus-4-5-thinking"
 EXECUTOR="google/antigravity-claude-sonnet-4-5-thinking"
 DEBUGGER="google/antigravity-claude-sonnet-4-5-thinking"
 VALIDATOR="google/antigravity-claude-sonnet-4-5-thinking"
elif [ "$PRESET" = "balanced" ]; then
 PLANNER="zai-coding-plan/glm-4.7"
 PLAN_CHECKER="google/antigravity-gemini-3-flash"
 RESEARCHER="opencode/minimax-m2.5-free"
 RESEARCH_SYNTHESIZER="zai-coding-plan/glm-4.7"
 CODEBASE_MAPPER="zai-coding-plan/glm-4.7"
 EXECUTOR="opencode/minimax-m2.5-free"
 DEBUGGER="opencode/minimax-m2.5-free"
 VALIDATOR="google/antigravity-gemini-3-flash"
elif [ "$PRESET" = "budget" ]; then
 PLANNER="zai-coding-plan/glm-4.7"
 PLAN_CHECKER="zai-coding-plan/glm-4.7"
 RESEARCHER="opencode/minimax-m2.5-free"
 RESEARCH_SYNTHESIZER="zai-coding-plan/glm-4.7"
 CODEBASE_MAPPER="zai-coding-plan/glm-4.7"
 EXECUTOR="opencode/minimax-m2.5-free"
 DEBUGGER="opencode/minimax-m2.5-free"
 VALIDATOR="zai-coding-plan/glm-4.7"
fi

echo "chosen preset: $PRESET \
 PLANNER=$PLANNER \
 PLAN_CHECKER=$PLAN_CHECKER \
 RESEARCHER=$RESEARCHER \
 RESEARCH_SYNTHESIZER=$RESEARCH_SYNTHESIZER \
 CODEBASE_MAPPER=$CODEBASE_MAPPER \
 EXECUTOR=$EXECUTOR \
 DEBUGGER=$DEBUGGER \
 VALIDATOR=$VALIDATOR \
"

cat > opencode.json << EOF
{
  "\$schema": "https://opencode.ai/config.json",
  "agent": {
    "gsd-planner": { "model": "$PLANNER" },
    "gsd-plan-checker": { "model": "$PLAN_CHECKER" },
    "gsd-phase-researcher": { "model": "$RESEARCHER" },
    "gsd-roadmapper": { "model": "$PLANNER" },
    "gsd-project-researcher": { "model": "$RESEARCHER" },
    "gsd-research-synthesizer": { "model": "$RESEARCH_SYNTHESIZER" },
    "gsd-codebase-mapper": { "model": "$CODEBASE_MAPPER" },
    "gsd-executor": { "model": "$EXECUTOR" },
    "gsd-debugger": { "model": "$DEBUGGER" },
    "gsd-verifier": { "model": "$VALIDATOR" },
    "gsd-integration-checker": { "model": "$VALIDATOR" },
    "gsd-set-profile": { "model": "$SETTINGS" },
    "gsd-settings": { "model": "$SETTINGS" },
    "gsd-set-model": { "model": "$SETTINGS" }
  }
}
EOF