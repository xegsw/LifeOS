(() => {
  const text = document.querySelector('#capture-text');
  const status = document.querySelector('#capture-status');
  const record = document.querySelector('#saved-record');
  const output = document.querySelector('#saved-text');
  const clear = (message) => { if (record) record.hidden = true; if (output) output.textContent = ''; if (status) status.textContent = message; };
  document.querySelector('#confirm-save')?.addEventListener('click', () => {
    const value = text.value.trim();
    if (!value) return clear('未显示记录：请先输入原文，再明确确认。');
    output.textContent = value; record.hidden = false;
    status.textContent = '已确认：仅显示在本次页面会话；刷新或关闭后会清除。';
  });
  document.querySelector('#simulate-failure')?.addEventListener('click', () => clear('模拟失败：本次会话未保留或显示原文，请核对后重试。'));
  document.querySelector('#choose-project')?.addEventListener('click', () => { document.querySelector('#no-suggestion-status').textContent = '选择 Project 是受控路径；本页不打开或读取任何资料。'; });
  document.querySelector('#record-stop')?.addEventListener('click', () => { document.querySelector('#no-suggestion-status').textContent = '先记录当前停点是受控路径；可切换到默认恢复页后手动输入原文。'; });
})();
