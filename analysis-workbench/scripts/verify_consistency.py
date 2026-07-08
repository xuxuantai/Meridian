#!/usr/bin/env python3
"""
Analysis Workbench — 一致性校验脚本

用法:
    python verify_consistency.py <analysis_dir>

检查项:
    1. contract.yaml 中所有 locked 条目是否完整
    2. state.yaml 中结论的依赖链是否有环
    3. state.yaml 中结论引用的 metrics 是否在 contract.yaml 中存在
    4. changelog.md 是否存在
"""

import sys
import os
import yaml
import re
from collections import defaultdict


def load_yaml(path):
    with open(path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def check_metric_references(contract, state):
    """检查 state 中结论引用的 metrics 是否在 contract 中定义"""
    issues = []
    
    contract_metric_ids = set()
    for m in contract.get('metrics', []) or []:
        contract_metric_ids.add(m['id'])
    
    for c in state.get('conclusions', []) or []:
        for mid in c.get('metrics_used', []) or []:
            if mid not in contract_metric_ids:
                issues.append(
                    f"结论 {c['id']} 引用了未定义的指标 '{mid}'"
                )
    
    return issues


def check_dependency_chain(state):
    """检查结论依赖链是否有环"""
    issues = []
    
    conclusions = state.get('conclusions', []) or []
    conclusion_ids = {c['id'] for c in conclusions}
    dep_graph = {}
    
    for c in conclusions:
        dep_graph[c['id']] = c.get('depends_on', []) or []
    
    # Check for references to non-existent conclusions
    for cid, deps in dep_graph.items():
        for dep in deps:
            if dep not in conclusion_ids:
                issues.append(f"结论 {cid} 依赖了不存在的结论 '{dep}'")
    
    # Check for cycles (DFS)
    WHITE, GRAY, BLACK = 0, 1, 2
    color = defaultdict(int)
    
    def dfs(node):
        color[node] = GRAY
        for dep in dep_graph.get(node, []):
            if dep not in conclusion_ids:
                continue
            if color[dep] == GRAY:
                issues.append(f"结论依赖链存在环: {node} → {dep}")
                return
            if color[dep] == WHITE:
                dfs(dep)
        color[node] = BLACK
    
    for cid in conclusion_ids:
        if color[cid] == WHITE:
            dfs(cid)
    
    return issues


def check_locked_consistency(state):
    """检查已锁定的结论是否都有 evidence"""
    issues = []
    
    for c in state.get('conclusions', []) or []:
        if c.get('locked', False):
            if not c.get('evidence'):
                issues.append(f"已锁定结论 {c['id']} 缺少 evidence")
            if not c.get('statement'):
                issues.append(f"已锁定结论 {c['id']} 缺少 statement")
    
    return issues


def check_contract_completeness(contract):
    """检查 contract 中 locked 条目的完整性"""
    issues = []
    
    for m in contract.get('metrics', []) or []:
        if m.get('locked', False):
            if not m.get('definition'):
                issues.append(f"已锁定指标 '{m['id']}' 缺少 definition")
            if not m.get('formula'):
                issues.append(f"已锁定指标 '{m['id']}' 缺少 formula")
    
    for dc in contract.get('data_constraints', []) or []:
        if dc.get('locked', False):
            if not dc.get('rule'):
                issues.append(f"已锁定约束 '{dc['id']}' 缺少 rule")
    
    return issues


def check_changelog_exists(analysis_dir):
    """检查 changelog 是否存在"""
    changelog_path = os.path.join(analysis_dir, 'changelog.md')
    if not os.path.exists(changelog_path):
        return ["changelog.md 不存在"]
    return []


def main():
    if len(sys.argv) < 2:
        print("用法: python verify_consistency.py <analysis_dir>")
        print("示例: python verify_consistency.py .analysis")
        sys.exit(1)
    
    analysis_dir = sys.argv[1]
    
    if not os.path.isdir(analysis_dir):
        print(f"错误: 目录 '{analysis_dir}' 不存在")
        sys.exit(1)
    
    contract_path = os.path.join(analysis_dir, 'contract.yaml')
    state_path = os.path.join(analysis_dir, 'state.yaml')
    
    all_issues = []
    
    # Check changelog
    all_issues.extend(check_changelog_exists(analysis_dir))
    
    # Load files
    contract = None
    state = None
    
    if os.path.exists(contract_path):
        contract = load_yaml(contract_path)
    else:
        all_issues.append("contract.yaml 不存在")
    
    if os.path.exists(state_path):
        state = load_yaml(state_path)
    else:
        all_issues.append("state.yaml 不存在")
    
    if contract:
        all_issues.extend(check_contract_completeness(contract))
    
    if state:
        all_issues.extend(check_locked_consistency(state))
        all_issues.extend(check_dependency_chain(state))
        
        if contract:
            all_issues.extend(check_metric_references(contract, state))
    
    # Output results
    phase = contract.get('meta', {}).get('phase', 'unknown') if contract else 'unknown'
    print(f"=== Analysis Workbench 一致性校验 ===")
    print(f"分析阶段: {phase}")
    print(f"检查时间: {__import__('datetime').datetime.now().isoformat()}")
    print()
    
    if all_issues:
        print(f"发现 {len(all_issues)} 个问题:\n")
        for i, issue in enumerate(all_issues, 1):
            print(f"  {i}. ⚠ {issue}")
        sys.exit(1)
    else:
        print("✓ 所有检查通过")
        sys.exit(0)


if __name__ == '__main__':
    main()
