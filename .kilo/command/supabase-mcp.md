# Supabase MCP Server

Add the Supabase MCP server to your project config:

```bash
claude mcp add --scope project --transport http supabase "https://mcp.supabase.com/mcp?project_ref=muzemjdlrxuewvcdwxpm&features=docs%2Caccount%2Cdatabase%2Cdebugging%2Cdevelopment%2Cfunctions%2Cbranching"
```

After configuring, authenticate:

```bash
claude /mcp
```

Select the `supabase` server, then **Authenticate** to begin the flow.

Project reference: `muzemjdlrxuewvcdwxpm`
Base URL: `https://muzemjdlrxuewvcdwxpm.supabase.co`

## Agent Skills (optional)

Install Supabase agent skills for faster, more accurate agentic work:

```bash
npx skills add supabase/agent-skills
```
