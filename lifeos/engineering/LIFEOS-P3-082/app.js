(() => {
  const states = [...document.querySelectorAll('.page-state')];
  const switchers = [...document.querySelectorAll('[data-state]')];
  const text = document.querySelector('#capture-text');
  const status = document.querySelector('#capture-status');
  const record = document.querySelector('#saved-record');
  const savedText = document.querySelector('#saved-text');

  function selectState(id) {
    states.forEach((state) => { state.hidden = state.id !== id; });
    switchers.forEach((button) => button.setAttribute('aria-pressed', String(button.dataset.state === id)));
  }
  switchers.forEach((button) => button.addEventListener('click', () => selectState(button.dataset.state)));

  document.querySelector('#confirm-save').addEventListener('click', () => {
    const value = text.value.trim();
    if (!value) { status.textContent = '未保存：请输入原文后再显式确认。'; record.hidden = true; return; }
    savedText.textContent = value;
    record.hidden = false;
    status.textContent = '已确认：已保留在本次页面会话；刷新或关闭后会丢弃。';
  });
  document.querySelector('#simulate-failure').addEventListener('click', () => {
    record.hidden = true;
    status.textContent = '保存失败：本次会话未保留原文，请核对后重试。';
  });
  document.querySelector('#choose-project').addEventListener('click', () => {
    document.querySelector('#no-suggestion-status').textContent = '选择 Project 是受控路径；此验证页不打开或读取任何资料。';
  });
  document.querySelector('#record-stop').addEventListener('click', () => {
    document.querySelector('#no-suggestion-status').textContent = '先记录当前停点是受控路径；请切回默认恢复态后手动输入原文。';
  });
})();
