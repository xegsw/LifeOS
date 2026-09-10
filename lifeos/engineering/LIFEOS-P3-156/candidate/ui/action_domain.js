const clean = (s)=>s.trim().replace(/[。！!]+$/u, '').trim();
const forbidden = (s)=>/[“”"「」『』\n？?]/u.test(s) || [
        '如果',
        '假如',
        '假设',
        '他说',
        '她说',
        '引用',
        '是否',
        '吗',
        '可能',
        '也许',
        '举例',
        '比如',
        '例如',
        '希望',
        '据说',
        '考虑',
        '正在',
        '已经',
        '很累',
        '还没',
        '没做',
        '不是',
        '不打算',
        '不想',
        '不要'
    ].some((w)=>s.includes(w)) || s.includes('不') && !s.endsWith('先不做了');
const clearArrangement = (s)=>[
        '整理',
        '完善',
        '修复',
        '核对',
        '写',
        '阅读',
        '散步',
        '走路',
        '跑步',
        '联系',
        '完成',
        '处理',
        '复习',
        '练习',
        '做',
        '开会',
        '发送',
        '发邮件'
    ].some((v)=>s.replace(/^(那)?我/u, '').replace(/^(明天|今天|接下来|打算)/u, '').replace(/^(下午|上午|晚上)/u, '').replace(/^(先|要)/u, '').startsWith(v));
function matches(s, items) {
    s = clean(s).replace(/^(把|我)/u, '');
    if (!s || [
        '这个',
        '那个',
        '这件事'
    ].includes(s)) return [];
    return items.filter((a)=>a.confirmedContent.includes(s) || s.includes(a.confirmedContent));
}
export function actionCandidate(p) {
    const raw = p.raw, s = clean(raw), base = {
        rawSpan: {
            start: 0,
            end: raw.length
        },
        sourceRefs: []
    };
    if (!s || forbidden(s)) return;
    const pending = p.pending;
    const active = p.actions.filter((a)=>a.status === 'planned');
    const current = active.length ? active : p.actions;
    if (pending && [
        'complete',
        'cancel',
        'adjust'
    ].includes(pending.intendedOperation)) {
        const selected = matches(s.endsWith('那个') ? s.slice(0, -2) : s, p.actions.filter((a)=>pending.targetIds.includes(a.id)));
        if (selected.length === 1) {
            const a = selected[0];
            return {
                ...base,
                operation: pending.intendedOperation,
                targetId: a.id,
                expectedVersion: pending.versions[a.id],
                ...pending.content ? {
                    content: pending.content
                } : {},
                questionId: pending.id
            };
        }
    }
    let op = '', target = '', content = '';
    for (const [suffix, operation] of [
        [
            '做完了',
            'complete'
        ],
        [
            '完成了',
            'complete'
        ],
        [
            '先不做了',
            'cancel'
        ],
        [
            '取消了',
            'cancel'
        ]
    ])if (s.endsWith(suffix)) {
        op = operation;
        target = s.slice(0, -suffix.length);
        break;
    }
    if (!op && s.startsWith('把') && s.includes('改成')) {
        op = 'adjust';
        [target, content] = s.slice(1).split('改成');
    }
    if (!op && s.startsWith('把') && s.includes('改到')) {
        op = 'adjust';
        [target, content] = s.slice(1).split('改到');
        content = target + '，' + content;
    }
    if (op) {
        let found = matches(target, p.actions);
        if (!target || [
            '这个',
            '那个',
            '这件事'
        ].includes(target)) found = current.length === 1 ? current : [];
        if (found.length === 1) {
            const a = found[0];
            return {
                ...base,
                operation: op,
                targetId: a.id,
                expectedVersion: a.version,
                ...op === 'adjust' ? {
                    content
                } : {}
            };
        }
        return {
            ...base,
            operation: 'clarify',
            intendedOperation: op,
            targetIds: p.actions.map((a)=>a.id),
            ...content ? {
                content
            } : {},
            question: '你指的是哪件安排？请说出它的内容。'
        };
    }
    if (s === '好了' || s === '这个') return {
        ...base,
        operation: 'clarify',
        intendedOperation: 'unknown',
        targetIds: p.actions.map((a)=>a.id),
        question: '你指哪件事，想怎样调整它？'
    };
    if ([
        '我明天',
        '我今天',
        '我接下来',
        '我打算',
        '那我明天',
        '那我今天'
    ].some((prefix)=>s.startsWith(prefix)) && !s.includes('可以') && !s.includes('想聊')) {
        if (s.includes('这个') || s.includes('那个')) {
            if (p.suggestions.length !== 1) return {
                ...base,
                operation: 'clarify',
                intendedOperation: 'create',
                targetIds: [],
                question: '你想记下哪件安排？请直接说出内容。'
            };
            const suggestion = p.suggestions[0];
            return {
                ...base,
                operation: 'create',
                content: s.replace('这个', suggestion.content).replace('那个', suggestion.content),
                sourceRefs: suggestion.sourceRefs
            };
        }
        if (s.length > 4 && !s.endsWith('了') && (!(s.startsWith('我今天') || s.startsWith('那我今天')) || s.includes('先') || s.includes('要')) && clearArrangement(s)) return {
            ...base,
            operation: 'create',
            content: s
        };
    }
    return;
}
export function validateCandidate(p, c, at = Date.now()) {
    if (p.expiresAt <= at) throw {
        code: 'action_context_stale'
    };
    const expected = actionCandidate(p);
    if (!expected || JSON.stringify(expected) !== JSON.stringify(c)) throw {
        code: 'action_candidate_rejected'
    };
    if (c.operation !== 'create' && c.operation !== 'clarify') {
        const a = p.actions.find((a)=>a.id === c.targetId);
        if (!a || a.version !== c.expectedVersion) throw {
            code: 'action_version_conflict'
        };
        if (a.status !== 'planned') throw {
            code: 'action_terminal'
        };
    }
    if (c.operation === 'adjust' && !c.content?.trim()) throw {
        code: 'action_candidate_rejected'
    };
    return c;
}
export function transition(a, c, identity) {
    if (c.operation === 'clarify') throw {
        code: 'action_candidate_rejected'
    };
    if (a && (a.status !== 'planned' || a.version !== c.expectedVersion)) throw {
        code: 'action_version_conflict'
    };
    return {
        id: a?.id || identity.id,
        version: (a?.version || 0) + 1,
        confirmedContent: c.content || a.confirmedContent,
        status: c.operation === 'complete' ? 'completed' : c.operation === 'cancel' ? 'cancelled' : 'planned',
        createdAt: a?.createdAt || identity.at,
        updatedAt: identity.at,
        confirmationRawRef: identity.rawId,
        sourceRefs: c.operation === 'create' ? c.sourceRefs : a.sourceRefs,
        basisStatus: a?.basisStatus || 'valid'
    };
}
