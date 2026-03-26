# HEARTBEAT.md - Periodic Tasks

## Daily Checks

### Morning (09:00)
- [ ] Check GitHub issues and PRs
- [ ] Review Discord/Telegram messages
- [ ] Check overnight simulation runs

### Evening (18:00)
- [ ] Update daily progress in `memory/YYYY-MM-DD.md`
- [ ] Sync with team on progress
- [ ] Plan next day's tasks

## Weekly Tasks

### Monday
- [ ] Review weekly goals
- [ ] Update project roadmap
- [ ] Check skill functionality

### Friday
- [ ] Weekly summary
- [ ] Update documentation
- [ ] Backup important data

## Project-Specific Tasks

### XinHaiAgents Framework
- [ ] Monitor simulation performance
- [ ] Check agent response quality
- [ ] Review visualization outputs

### Skills Maintenance
- [ ] Test `xinhai-agents` skill
- [ ] Test `suicide-risk-evidence` skill
- [ ] Update scenario templates if needed

### Research Tasks
- [ ] Check latest multi-agent papers
- [ ] Review mental health AI developments
- [ ] Track CLPsych/ACL conferences

## Automated Tasks

### Daily Paper Tracking
```
Search: arXiv multi-agent simulation
Search: arXiv mental health LLM
Search: arXiv suicide prevention AI
```

### Weekly Benchmark
```
Run: Evaluation scripts for skills
Compare: Performance metrics
Report: Any regressions
```

## Emergency Checks

### High Priority
- [ ] Critical bug in simulation
- [ ] Safety issue in risk detection
- [ ] Service downtime

### Response Actions
1. Assess severity
2. Notify team immediately
3. Implement fix
4. Document incident

## Heartbeat State

Track last checks in `memory/heartbeat-state.json`:

```json
{
  "lastChecks": {
    "github_issues": "2024-03-26T09:00:00Z",
    "skill_tests": "2024-03-26T09:00:00Z",
    "paper_search": "2024-03-26T09:00:00Z"
  }
}
```

## Keep Empty When Idle

If nothing needs attention, keep this file minimal to reduce context usage.
