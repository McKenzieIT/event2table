#!/usr/bin/env python3
"""
Generate test configurations for all 34 Event2Table pages
"""

import json
import os

# All 34 pages with their URLs and testing requirements
PAGES = [
    # Dashboard & Home (1 page)
    {
        "id": "REG-001",
        "name": "Dashboard Load Test",
        "url": "http://localhost:5173/",
        "module": "dashboard",
        "priority": "critical",
        "selectors": [".dashboard-container", ".stat-card", ".action-card"]
    },

    # Games Management (1 page)
    {
        "id": "REG-002",
        "name": "Games List Display",
        "url": "http://localhost:5173/games",
        "module": "games",
        "priority": "critical",
        "selectors": [".games-grid", "input[placeholder*='搜索']", ".game-card"]
    },

    # Events Management (4 pages)
    {
        "id": "REG-003",
        "name": "Events List Display",
        "url": "http://localhost:5173/events",
        "module": "events",
        "priority": "critical",
        "selectors": [".events-table", ".pagination"]
    },
    {
        "id": "REG-004",
        "name": "Event Create Form",
        "url": "http://localhost:5173/events/create",
        "module": "events",
        "priority": "high",
        "selectors": ["#event-name-input", "#event-table-input", "#event-type-select", ".submit-button"]
    },
    {
        "id": "REG-005",
        "name": "Event Detail Page",
        "url": "http://localhost:5173/events/1",
        "module": "events",
        "priority": "high",
        "selectors": [".event-detail", ".event-info", ".related-events"]
    },
    {
        "id": "REG-006",
        "name": "Event Edit Form",
        "url": "http://localhost:5173/events/1/edit",
        "module": "events",
        "priority": "high",
        "selectors": ["#event-name-input", "#event-table-input", ".update-button"]
    },

    # Parameters Management (9 pages)
    {
        "id": "REG-007",
        "name": "Parameters List",
        "url": "http://localhost:5173/parameters",
        "module": "parameters",
        "priority": "critical",
        "selectors": [".parameters-table", ".filter-controls"]
    },
    {
        "id": "REG-008",
        "name": "Parameters Enhanced",
        "url": "http://localhost:5173/parameters/enhanced",
        "module": "parameters",
        "priority": "high",
        "selectors": [".enhanced-table", ".batch-actions"]
    },
    {
        "id": "REG-009",
        "name": "Parameter Dashboard",
        "url": "http://localhost:5173/parameters/dashboard",
        "module": "parameters",
        "priority": "high",
        "selectors": [".dashboard-charts", ".parameter-stats"]
    },
    {
        "id": "REG-010",
        "name": "Parameter Compare",
        "url": "http://localhost:5173/parameters/compare",
        "module": "parameters",
        "priority": "medium",
        "selectors": [".comparison-table", ".diff-view"]
    },
    {
        "id": "REG-011",
        "name": "Parameter Analysis",
        "url": "http://localhost:5173/parameter-analysis",
        "module": "parameters",
        "priority": "medium",
        "selectors": [".analysis-charts", ".insight-cards"]
    },
    {
        "id": "REG-012",
        "name": "Parameter Usage",
        "url": "http://localhost:5173/parameter-usage",
        "module": "parameters",
        "priority": "medium",
        "selectors": [".usage-table", ".usage-charts"]
    },
    {
        "id": "REG-013",
        "name": "Parameter History",
        "url": "http://localhost:5173/parameter-history",
        "module": "parameters",
        "priority": "medium",
        "selectors": [".history-timeline", ".version-list"]
    },
    {
        "id": "REG-014",
        "name": "Parameter Network",
        "url": "http://localhost:5173/parameter-network",
        "module": "parameters",
        "priority": "low",
        "selectors": [".network-graph", ".node-details"]
    },
    {
        "id": "REG-015",
        "name": "Common Parameters",
        "url": "http://localhost:5173/common-params",
        "module": "parameters",
        "priority": "medium",
        "selectors": [".common-params-table", ".param-definitions"]
    },

    # Event Nodes & Canvas (6 pages)
    {
        "id": "REG-016",
        "name": "Canvas Page",
        "url": "http://localhost:5173/canvas",
        "module": "canvas",
        "priority": "critical",
        "selectors": [".canvas-container", ".node-palette"]
    },
    {
        "id": "REG-017",
        "name": "Event Node Builder",
        "url": "http://localhost:5173/event-node-builder",
        "module": "canvas",
        "priority": "critical",
        "selectors": [".node-builder", ".config-panel"]
    },
    {
        "id": "REG-018",
        "name": "Event Nodes List",
        "url": "http://localhost:5173/event-nodes",
        "module": "canvas",
        "priority": "high",
        "selectors": [".nodes-list", ".node-filters"]
    },
    {
        "id": "REG-019",
        "name": "Field Builder",
        "url": "http://localhost:5173/field-builder",
        "module": "canvas",
        "priority": "high",
        "selectors": [".field-builder", ".field-config"]
    },
    {
        "id": "REG-020",
        "name": "Flow Builder",
        "url": "http://localhost:5173/flow-builder",
        "module": "canvas",
        "priority": "high",
        "selectors": [".flow-canvas", ".flow-controls"]
    },
    {
        "id": "REG-021",
        "name": "Flows List",
        "url": "http://localhost:5173/flows",
        "module": "canvas",
        "priority": "high",
        "selectors": [".flows-list", ".flow-status"]
    },

    # HQL Generation (5 pages)
    {
        "id": "REG-022",
        "name": "HQL Manage",
        "url": "http://localhost:5173/hql-manage",
        "module": "hql",
        "priority": "critical",
        "selectors": [".hql-list", ".hql-actions"]
    },
    {
        "id": "REG-023",
        "name": "HQL Results",
        "url": "http://localhost:5173/hql-results",
        "module": "hql",
        "priority": "high",
        "selectors": [".results-table", ".export-controls"]
    },
    {
        "id": "REG-024",
        "name": "HQL Edit",
        "url": "http://localhost:5173/hql/1/edit",
        "module": "hql",
        "priority": "high",
        "selectors": [".hql-editor", ".preview-panel"]
    },
    {
        "id": "REG-025",
        "name": "Generate HQL",
        "url": "http://localhost:5173/generate",
        "module": "hql",
        "priority": "high",
        "selectors": [".generate-wizard", ".step-indicator"]
    },
    {
        "id": "REG-026",
        "name": "Generate Result",
        "url": "http://localhost:5173/generate/result",
        "module": "hql",
        "priority": "high",
        "selectors": [".result-display", ".download-links"]
    },

    # Other Features (8 pages)
    {
        "id": "REG-027",
        "name": "Categories List",
        "url": "http://localhost:5173/categories",
        "module": "other",
        "priority": "medium",
        "selectors": [".categories-table", ".category-tree"]
    },
    {
        "id": "REG-028",
        "name": "Import Events",
        "url": "http://localhost:5173/import-events",
        "module": "other",
        "priority": "medium",
        "selectors": [".import-form", ".file-upload"]
    },
    {
        "id": "REG-029",
        "name": "Batch Operations",
        "url": "http://localhost:5173/batch-operations",
        "module": "other",
        "priority": "medium",
        "selectors": [".batch-controls", ".operation-list"]
    },
    {
        "id": "REG-030",
        "name": "Create Log",
        "url": "http://localhost:5173/logs/create",
        "module": "other",
        "priority": "low",
        "selectors": [".log-form", ".log-fields"]
    },
    {
        "id": "REG-031",
        "name": "Log Detail",
        "url": "http://localhost:5173/log-detail",
        "module": "other",
        "priority": "low",
        "selectors": [".log-detail", ".log-metadata"]
    },
    {
        "id": "REG-032",
        "name": "Alter SQL",
        "url": "http://localhost:5173/alter-sql/123",
        "module": "other",
        "priority": "low",
        "selectors": [".sql-editor", ".preview-panel"]
    },
    {
        "id": "REG-033",
        "name": "API Documentation",
        "url": "http://localhost:5173/api-docs",
        "module": "other",
        "priority": "low",
        "selectors": [".api-docs", ".endpoint-list"]
    },
    {
        "id": "REG-034",
        "name": "Validation Rules",
        "url": "http://localhost:5173/validation-rules",
        "module": "other",
        "priority": "low",
        "selectors": [".rules-list", ".rule-editor"]
    }
]

def generate_test_config(page):
    """Generate test configuration for a page"""

    # Build validation checks
    checks = [
        {"type": "console_clean", "level": "error"}
    ]

    # Add element existence checks for each selector
    for selector in page.get("selectors", []):
        checks.append({"type": "element_exists", "selector": selector})

    # Build test steps
    steps = [
        {
            "action": "open",
            "url": page["url"]
        },
        {
            "action": "wait",
            "condition": {"load": "networkidle"}
        }
    ]

    # Add snapshot for pages with interactive elements
    if page["priority"] in ["critical", "high"]:
        steps.append({
            "action": "snapshot",
            "saveRefs": True
        })

    # Add validation
    steps.append({
        "action": "validate",
        "checks": checks
    })

    # Add screenshot
    screenshot_name = page["name"].lower().replace(" ", "_")
    steps.append({
        "action": "screenshot",
        "path": f"output/screenshots/regression/{page['module']}/{screenshot_name}.png"
    })

    # Create test config
    test_config = {
        "id": page["id"],
        "name": page["name"],
        "type": "regression",
        "priority": page["priority"],
        "engine": "agent-browser",
        "url": page["url"],
        "timeout": 10000,
        "module": page["module"],
        "steps": steps
    }

    return test_config

def main():
    # Output directory
    output_dir = "/Users/mckenzie/Documents/event2table/.claude/skills/event2table-universal-test/tests/regression"
    os.makedirs(output_dir, exist_ok=True)

    # Create module subdirectories
    modules = set(page["module"] for page in PAGES)
    for module in modules:
        os.makedirs(os.path.join(output_dir, module), exist_ok=True)

    # Generate tests
    generated = 0
    for page in PAGES:
        test_config = generate_test_config(page)

        # Save to file
        filename = f"{page['id'].lower()}.json"
        filepath = os.path.join(output_dir, page["module"], filename)

        with open(filepath, 'w') as f:
            json.dump(test_config, f, indent=2)

        generated += 1
        print(f"✓ Generated: {page['id']} - {page['name']}")

    print(f"\n✅ Total tests generated: {generated}")
    print(f"📁 Location: {output_dir}")

    # Generate summary
    summary = {
        "total_tests": len(PAGES),
        "by_module": {},
        "by_priority": {}
    }

    for page in PAGES:
        module = page["module"]
        priority = page["priority"]

        summary["by_module"][module] = summary["by_module"].get(module, 0) + 1
        summary["by_priority"][priority] = summary["by_priority"].get(priority, 0) + 1

    summary_file = os.path.join(output_dir, "_summary.json")
    with open(summary_file, 'w') as f:
        json.dump(summary, f, indent=2)

    print(f"📊 Summary saved to: {summary_file}")

if __name__ == "__main__":
    main()
