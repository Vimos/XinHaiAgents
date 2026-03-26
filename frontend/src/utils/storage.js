/**
 * 对话历史存储管理
 * 使用 localStorage 实现客户端存储
 */

const STORAGE_KEY_PREFIX = 'xinhai_chat_';

/**
 * 生成会话ID
 */
export function generateSessionId() {
  return `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
}

/**
 * 保存对话历史
 * @param {string} sessionId - 会话ID
 * @param {Array} messages - 消息数组
 */
export function saveChatHistory(sessionId, messages) {
  try {
    const key = STORAGE_KEY_PREFIX + sessionId;
    const data = {
      messages,
      timestamp: Date.now(),
      lastUpdated: new Date().toISOString()
    };
    localStorage.setItem(key, JSON.stringify(data));
    console.log('[Storage] Saved chat history:', sessionId, messages.length, 'messages');
  } catch (error) {
    console.error('[Storage] Failed to save chat history:', error);
  }
}

/**
 * 加载对话历史
 * @param {string} sessionId - 会话ID
 * @returns {Array|null} 消息数组
 */
export function loadChatHistory(sessionId) {
  try {
    const key = STORAGE_KEY_PREFIX + sessionId;
    const data = localStorage.getItem(key);
    if (!data) return null;
    
    const parsed = JSON.parse(data);
    console.log('[Storage] Loaded chat history:', sessionId, parsed.messages?.length, 'messages');
    return parsed.messages || [];
  } catch (error) {
    console.error('[Storage] Failed to load chat history:', error);
    return null;
  }
}

/**
 * 删除对话历史
 * @param {string} sessionId - 会话ID
 */
export function deleteChatHistory(sessionId) {
  try {
    const key = STORAGE_KEY_PREFIX + sessionId;
    localStorage.removeItem(key);
    console.log('[Storage] Deleted chat history:', sessionId);
  } catch (error) {
    console.error('[Storage] Failed to delete chat history:', error);
  }
}

/**
 * 获取所有会话列表
 * @returns {Array} 会话列表
 */
export function getAllSessions() {
  try {
    const sessions = [];
    for (let i = 0; i < localStorage.length; i++) {
      const key = localStorage.key(i);
      if (key && key.startsWith(STORAGE_KEY_PREFIX)) {
        const sessionId = key.replace(STORAGE_KEY_PREFIX, '');
        const data = JSON.parse(localStorage.getItem(key));
        
        // 获取第一条用户消息作为标题
        const firstUserMsg = data.messages?.find(m => m.role === 'user');
        const title = firstUserMsg 
          ? firstUserMsg.content.substring(0, 30) + '...'
          : '新对话';
        
        sessions.push({
          sessionId,
          title,
          timestamp: data.timestamp,
          lastUpdated: data.lastUpdated,
          messageCount: data.messages?.length || 0
        });
      }
    }
    
    // 按时间倒序排列
    return sessions.sort((a, b) => b.timestamp - a.timestamp);
  } catch (error) {
    console.error('[Storage] Failed to get sessions:', error);
    return [];
  }
}

/**
 * 清理旧会话（保留最近 N 个）
 * @param {number} keepCount - 保留数量
 */
export function cleanupOldSessions(keepCount = 20) {
  try {
    const sessions = getAllSessions();
    if (sessions.length <= keepCount) return;
    
    const toDelete = sessions.slice(keepCount);
    toDelete.forEach(session => {
      deleteChatHistory(session.sessionId);
    });
    
    console.log('[Storage] Cleaned up', toDelete.length, 'old sessions');
  } catch (error) {
    console.error('[Storage] Failed to cleanup sessions:', error);
  }
}

/**
 * 导出所有对话（备份）
 * @returns {Object} 所有对话数据
 */
export function exportAllChats() {
  try {
    const exportData = {
      exportTime: new Date().toISOString(),
      sessions: {}
    };
    
    for (let i = 0; i < localStorage.length; i++) {
      const key = localStorage.key(i);
      if (key && key.startsWith(STORAGE_KEY_PREFIX)) {
        const sessionId = key.replace(STORAGE_KEY_PREFIX, '');
        exportData.sessions[sessionId] = JSON.parse(localStorage.getItem(key));
      }
    }
    
    return exportData;
  } catch (error) {
    console.error('[Storage] Failed to export chats:', error);
    return null;
  }
}

/**
 * 导入对话（恢复）
 * @param {Object} data - 导出的数据
 */
export function importChats(data) {
  try {
    if (!data || !data.sessions) return false;
    
    Object.entries(data.sessions).forEach(([sessionId, sessionData]) => {
      const key = STORAGE_KEY_PREFIX + sessionId;
      localStorage.setItem(key, JSON.stringify(sessionData));
    });
    
    console.log('[Storage] Imported', Object.keys(data.sessions).length, 'sessions');
    return true;
  } catch (error) {
    console.error('[Storage] Failed to import chats:', error);
    return false;
  }
}
