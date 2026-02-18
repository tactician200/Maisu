---
name: n8n-workflow-builder
description: "Use this skill when building, debugging, or optimizing n8n automation workflows. Triggers include: creating new n8n workflows, connecting nodes, configuring AI agents, setting up webhooks, troubleshooting workflow errors, optimizing Claude model selection (Haiku/Sonnet/Opus) for cost-performance, implementing MCP integrations, or any task involving n8n automation. Also use for workflow architecture decisions, node configuration patterns, error handling strategies, and production deployment. Do NOT use for general coding tasks unrelated to n8n or for other automation platforms like Zapier or Make."
---

# n8n Workflow Builder

A skill for creating robust, production-ready n8n automation workflows with intelligent model selection and best practices from real-world deployments.

## Overview

This skill codifies patterns for building n8n workflows that are:
- **Reliable**: Proper error handling, retries, and fallback logic
- **Cost-efficient**: Smart Claude model selection (Haiku/Sonnet/Opus) based on task complexity
- **Maintainable**: Clear naming, documentation, and modular architecture
- **Scalable**: Patterns that work for 1000+ annual projects

## Quick Reference

| Task | Approach |
|------|----------|
| Create workflow | Use `n8n_create_workflow` with proper node structure |
| Add/modify nodes | Use `n8n_update_partial_workflow` for incremental changes |
| AI Agent setup | Language model FIRST, then agent, then tools |
| Validate before deploy | Always run `n8n_validate_workflow` |
| Debug errors | Use `n8n_executions` with mode='error' |

---

## Workflow Architecture Principles

### 1. Trigger Selection

Choose the right trigger for your use case:

| Trigger Type | Use When | Key Configuration |
|--------------|----------|-------------------|
| Webhook | External API calls, integrations | `responseMode: "onReceived"` or `"lastNode"` |
| Chat Trigger | Conversational AI interfaces | `responseMode: "streaming"` for real-time |
| Schedule | Periodic tasks, batch processing | Cron expression or interval |
| Manual | Testing and on-demand execution | N/A |

### 2. Node Naming Convention

Use consistent, descriptive names:

```
[Action] [Target] [Context]

Examples:
- "Parse Email Content"
- "Route by Priority Level"  
- "Format Slack Notification"
- "Validate Client Data"
- "AI Classify Message Intent"
```

### 3. Workflow Modularity

Structure complex workflows with clear sections:

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   TRIGGER   │ → │   INTAKE    │ → │  PROCESS    │ → │   OUTPUT    │
│             │    │  Validate   │    │  Transform  │    │  Deliver    │
│  Webhook    │    │  Parse      │    │  AI Logic   │    │  Notify     │
│  Schedule   │    │  Normalize  │    │  Route      │    │  Store      │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
```

---

## Claude Model Selection Strategy

### Decision Framework

Select models based on task complexity and cost sensitivity:

| Model | Best For | Cost Factor | Use Cases |
|-------|----------|-------------|-----------|
| **Haiku** | Simple, high-volume tasks | 1x (baseline) | Classification, extraction, formatting, routing |
| **Sonnet** | Balanced tasks | ~10x Haiku | Summarization, analysis, content generation |
| **Opus** | Complex reasoning | ~75x Haiku | Multi-step analysis, creative work, nuanced decisions |

### Implementation Pattern

```javascript
// Model selection node (Set node or Code node)
const taskComplexity = $input.item.json.complexity || 'simple';
const costSensitive = $input.item.json.high_volume || false;

let selectedModel = 'claude-sonnet-4-20250514'; // Default

if (taskComplexity === 'simple' || costSensitive) {
  selectedModel = 'claude-haiku-4-20250514';
} else if (taskComplexity === 'complex' || taskComplexity === 'creative') {
  selectedModel = 'claude-opus-4-20250514';
}

return { model: selectedModel };
```

### Cost Optimization Rules

1. **Default to Haiku** for:
   - Intent classification
   - Data extraction from structured formats
   - Simple reformatting
   - Yes/no decisions
   - Routing logic

2. **Use Sonnet** for:
   - Email summarization
   - Content analysis
   - Draft generation
   - Multi-field extraction
   - Moderate complexity reasoning

3. **Reserve Opus** for:
   - Complex document analysis
   - Creative writing that matters
   - Multi-step reasoning chains
   - Edge cases requiring nuance
   - High-stakes decisions

---

## AI Agent Configuration

### Essential Setup Order

**CRITICAL**: AI connections must follow this order:

1. Create Language Model node
2. Create AI Agent node
3. Connect Language Model → AI Agent (using `sourceOutput: "ai_languageModel"`)
4. Add and connect Tools
5. Add Memory if needed

### Minimal AI Agent Template

```javascript
// Using n8n_create_workflow
{
  name: "AI Agent Workflow",
  nodes: [
    {
      id: "trigger",
      name: "Chat Trigger",
      type: "@n8n/n8n-nodes-langchain.chatTrigger",
      typeVersion: 1.1,
      position: [0, 0],
      parameters: {
        options: {
          responseMode: "lastNode"
        }
      }
    },
    {
      id: "llm",
      name: "Claude Model",
      type: "@n8n/n8n-nodes-langchain.lmChatAnthropic",
      typeVersion: 1.3,
      position: [200, -100],
      parameters: {
        model: "claude-sonnet-4-20250514",
        maxTokens: 4096
      }
    },
    {
      id: "agent",
      name: "AI Agent",
      type: "@n8n/n8n-nodes-langchain.agent",
      typeVersion: 1.7,
      position: [200, 100],
      parameters: {
        promptType: "define",
        systemMessage: "You are a helpful assistant. Be concise and accurate."
      }
    }
  ],
  connections: {
    "Chat Trigger": {
      main: [[{ node: "AI Agent", type: "main", index: 0 }]]
    },
    "Claude Model": {
      ai_languageModel: [[{ node: "AI Agent", type: "ai_languageModel", index: 0 }]]
    }
  }
}
```

### Tool Configuration Best Practices

Every tool needs a clear description (15+ characters):

```javascript
// HTTP Request Tool
{
  name: "Fetch Project Data",
  type: "@n8n/n8n-nodes-langchain.toolHttpRequest",
  parameters: {
    toolDescription: "Retrieve project details from the database by project ID. Use when user asks about specific project status, deadlines, or assignments.",
    method: "GET",
    url: "https://api.example.com/projects/{projectId}",
    placeholderDefinitions: {
      values: [
        { name: "projectId", description: "Unique project identifier" }
      ]
    }
  }
}

// Code Tool
{
  name: "Calculate Deadline",
  type: "@n8n/n8n-nodes-langchain.toolCode",
  parameters: {
    name: "calculate_deadline",
    description: "Calculate project deadline based on complexity and team capacity. Returns estimated completion date.",
    language: "javaScript",
    code: `
      const baseWeeks = $input.complexity === 'high' ? 4 : 2;
      const teamFactor = 1 / Math.max($input.teamSize, 1);
      const weeks = Math.ceil(baseWeeks * teamFactor);
      const deadline = new Date();
      deadline.setDate(deadline.getDate() + (weeks * 7));
      return { deadline: deadline.toISOString(), weeks };
    `
  }
}
```

---

## Error Handling Patterns

### 1. Node-Level Error Handling

Enable on critical nodes:

```javascript
{
  type: "updateNode",
  nodeName: "Critical API Call",
  updates: {
    continueOnFail: true,  // Continue workflow on error
    retryOnFail: true,     // Retry on failure
    maxTries: 3,           // Number of retry attempts
    waitBetweenTries: 2000 // Milliseconds between retries
  }
}
```

### 2. Error Routing Pattern

Route errors to dedicated handling:

```
┌──────────────┐     Success    ┌──────────────┐
│  API Call    │ ─────────────→ │  Process     │
│              │                │  Response    │
└──────────────┘                └──────────────┘
       │
       │ Error (continueOnFail)
       ▼
┌──────────────┐    ┌──────────────┐
│  IF Error    │ →  │  Log Error   │
│  Detected    │    │  & Notify    │
└──────────────┘    └──────────────┘
```

### 3. Error Detection Code

```javascript
// In a Code node after a node with continueOnFail: true
const items = $input.all();
const errors = [];
const successes = [];

for (const item of items) {
  if (item.error) {
    errors.push({
      error: item.error.message,
      node: item.error.node,
      timestamp: new Date().toISOString()
    });
  } else {
    successes.push(item.json);
  }
}

return {
  successes,
  errors,
  hasErrors: errors.length > 0
};
```

---

## Webhook & MCP Integration

### Webhook Best Practices

```javascript
{
  name: "Webhook Receiver",
  type: "n8n-nodes-base.webhook",
  parameters: {
    path: "unique-path-identifier",  // Use descriptive, unique paths
    httpMethod: "POST",
    responseMode: "onReceived",      // Respond immediately
    responseCode: 200,
    options: {
      rawBody: true  // Preserve raw body for signature validation
    }
  }
}
```

### MCP Server Integration

For Claude MCP integration (like your n8n MCP server):

```javascript
// MCP Client Tool configuration
{
  name: "n8n MCP Tool",
  type: "@n8n/n8n-nodes-langchain.mcpClientTool",
  parameters: {
    description: "Manage n8n workflows - create, update, validate, and execute automation workflows",
    mcpServer: {
      transport: "sse",
      url: "https://your-n8n-instance.app.n8n.cloud/mcp-server/sse"
    },
    tool: "n8n_create_workflow"  // Or other n8n MCP tools
  }
}
```

---

## Production Checklist

### Before Activating a Workflow

- [ ] **Validation**: Run `n8n_validate_workflow` - fix all errors
- [ ] **Naming**: All nodes have descriptive names
- [ ] **Error Handling**: Critical paths have `continueOnFail` + error routing
- [ ] **Credentials**: All credentials configured and tested
- [ ] **AI Descriptions**: All tools have clear 15+ character descriptions
- [ ] **Model Selection**: Appropriate Claude model for task complexity
- [ ] **Rate Limits**: Consider API rate limits, add delays if needed
- [ ] **Testing**: Tested with real data via `n8n_test_workflow`

### Monitoring Setup

```javascript
// Add at workflow end for monitoring
{
  name: "Log Execution",
  type: "n8n-nodes-base.code",
  parameters: {
    jsCode: `
      const executionData = {
        workflowId: $workflow.id,
        executionId: $execution.id,
        timestamp: new Date().toISOString(),
        itemsProcessed: $input.all().length,
        success: true
      };
      
      // Send to your monitoring system
      return { execution: executionData };
    `
  }
}
```

---

## Common Patterns Library

### Pattern 1: Message Router (iArqui-style)

Route messages to different handlers based on classification:

```javascript
// Step 1: Classify with Haiku (fast, cheap)
{
  name: "Classify Intent",
  type: "@n8n/n8n-nodes-langchain.lmChatAnthropic",
  parameters: {
    model: "claude-haiku-4-20250514",
    systemPrompt: `Classify the message intent. Return ONLY one of:
    - URGENT: Requires immediate attention
    - PROJECT: Project-related query
    - BILLING: Financial/invoice question
    - SUPPORT: Technical support
    - OTHER: Doesn't fit other categories`
  }
}

// Step 2: Route with Switch node
{
  name: "Route by Intent",
  type: "n8n-nodes-base.switch",
  parameters: {
    rules: [
      { value: "URGENT", output: 0 },
      { value: "PROJECT", output: 1 },
      { value: "BILLING", output: 2 },
      { value: "SUPPORT", output: 3 }
    ],
    fallbackOutput: 4  // OTHER goes here
  }
}
```

### Pattern 2: Email Summarization Pipeline

```
┌──────────────┐    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│   Gmail      │ →  │  Filter by   │ →  │  Summarize   │ →  │   Format &   │
│   Trigger    │    │  Importance  │    │  with Sonnet │    │   Deliver    │
└──────────────┘    └──────────────┘    └──────────────┘    └──────────────┘
```

### Pattern 3: Batch Processing with Rate Limiting

```javascript
// Use SplitInBatches for large datasets
{
  name: "Process in Batches",
  type: "n8n-nodes-base.splitInBatches",
  parameters: {
    batchSize: 10,
    options: {
      reset: false
    }
  }
}

// Add Wait node for rate limiting
{
  name: "Rate Limit Delay",
  type: "n8n-nodes-base.wait",
  parameters: {
    amount: 1,
    unit: "seconds"
  }
}
```

---

## Debugging Workflows

### Execution Analysis

```javascript
// Get detailed error information
n8n_executions({
  action: "get",
  id: "execution_id",
  mode: "error",  // Optimized for debugging
  includeStackTrace: true,
  includeExecutionPath: true
})
```

### Common Issues & Solutions

| Issue | Diagnosis | Solution |
|-------|-----------|----------|
| AI Agent no response | Missing language model connection | Connect LM with `sourceOutput: "ai_languageModel"` |
| Webhook timeout | Processing too slow | Use `responseMode: "onReceived"` + async processing |
| Data not passing | Wrong expression syntax | Use `={{ $json.field }}` not `{{ $json.field }}` |
| Tool not called | Poor tool description | Make description specific about WHEN to use |
| High costs | Using Opus for simple tasks | Implement model selection logic |

### Auto-Fix Common Errors

```javascript
n8n_autofix_workflow({
  id: "workflow_id",
  applyFixes: true,
  fixTypes: [
    "expression-format",      // Fix expression syntax
    "typeversion-correction", // Update outdated typeVersions
    "error-output-config",    // Fix error handling config
    "webhook-missing-path"    // Add missing webhook paths
  ]
})
```

---

## Integration with Existing Tools

This skill works alongside the n8n MCP tools. When building workflows:

1. **Discovery**: Use `search_nodes` to find the right nodes
2. **Configuration**: Use `get_node` for parameter details
3. **Building**: Use `n8n_create_workflow` or `n8n_update_partial_workflow`
4. **Validation**: Always run `n8n_validate_workflow` before activating
5. **Testing**: Use `n8n_test_workflow` with sample data
6. **Debugging**: Use `n8n_executions` to analyze runs

---

## Version History

- **v1.0** (2025-02): Initial skill creation based on Tactician's production patterns
