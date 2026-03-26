/**
 * 对话历史存储管理 - 按边栏/路由隔离版本
 * 每个边栏（/chat, /cbt, /suicide-risk等）有独立的会话空间
 */

const STORAGE_KEY_PREFIX = 'xinhai_chat_';

/**
 * 生成会话ID
 * 格式: xinhai_{sidebar}_{timestamp}_{random}
 */
export function generateSessionId(sidebar = 'chat') {
  return `xinhai_${sidebar}_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
}

/**
 * 从 sessionId 解析边栏类型
 */
export function parseSidebarFromSessionId(sessionId) {
  if (!sessionId) return 'chat';
  const parts = sessionId.split('_');
  return parts[1] || 'chat';
}

/**
 * 保存对话历史
 * @param {string} sessionId - 会话ID
 * @param {string} sidebar - 边栏类型 (chat/cbt/suicide-risk等)
 * @param {Array} messages - 消息数组
 */
export function saveChatHistory(sessionId, sidebar, messages) {
  try {
    const key = STORAGE_KEY_PREFIX + sessionId;
    const data = {
      sessionId,
      sidebar,
      messages,
      timestamp: Date.now(),
      lastUpdated: new Date().toISOString()
    };
    localStorage.setItem(key, JSON.stringify(data));
    console.log(`[Storage] Saved [${sidebar}]:`, sessionId, messages.length, 'messages');
  } catch (error) {
    console.error('[Storage] Failed to save chat history:', error);
  }
}

/**
 * 加载对话历史
 * @param {string} sessionId - 会话ID
 * @returns {Object|null} 完整会话数据
 */
export function loadChatHistory(sessionId) {
  try {
    const key = STORAGE_KEY_PREFIX + sessionId;
    const data = localStorage.getItem(key);
    if (!data) return null;
    
    const parsed = JSON.parse(data);
    console.log(`[Storage] Loaded [${parsed.sidebar}]:`, sessionId, parsed.messages?.length, 'messages');
    return parsed;
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
    console.log('[Storage] Deleted:', sessionId);
  } catch (error) {
    console.error('[Storage] Failed to delete chat history:', error);
  }
}

/**
 * 获取指定边栏的所有会话列表
 * @param {string} sidebar - 边栏类型
 * @returns {Array} 会话列表
 */
export function getSessionsBySidebar(sidebar) {
  try {
    const sessions = [];
    for (let i = 0; i < localStorage.length; i++) {
      const key = localStorage.key(i);
      if (key && key.startsWith(STORAGE_KEY_PREFIX)) {
        const sessionId = key.replace(STORAGE_KEY_PREFIX, '');
        const data = JSON.parse(localStorage.getItem(key));
        
        // 只返回指定边栏的会话
        if (data.sidebar === sidebar) {
          // 获取第一条用户消息作为标题
          const firstUserMsg = data.messages?.find(m => m.role === 'user');
          const title = firstUserMsg 
            ? firstUserMsg.content.substring(0, 30) + '...'
            : '新对话';
          
          sessions.push({
            sessionId,
            sidebar: data.sidebar,
            title,
            timestamp: data.timestamp,
            lastUpdated: data.lastUpdated,
            messageCount: data.messages?.length || 0
          });
        }
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
 * 获取所有边栏的会话统计
 * @returns {Object} 各边栏会话数量
 */
export function getSidebarStats() {
  const stats = {};
  try {
    for (let i = 0; i < localStorage.length; i++) {
      const key = localStorage.key(i);
      if (key && key.startsWith(STORAGE_KEY_PREFIX)) {
        const data = JSON.parse(localStorage.getItem(key));
        const sidebar = data.sidebar || 'chat';
        stats[sidebar] = (stats[sidebar] || 0) + 1;
      }
    }
  } catch (error) {
    console.error('[Storage] Failed to get stats:', error);
  }
  return stats;
}

/**
 * 清理旧会话（保留最近 N 个）
 * @param {string} sidebar - 边栏类型
 * @param {number} keepCount - 保留数量
 */
export function cleanupOldSessions(sidebar, keepCount = 10) {
  try {
    const sessions = getSessionsBySidebar(sidebar);
    if (sessions.length <= keepCount) return;
    
    const toDelete = sessions.slice(keepCount);
    toDelete.forEach(session => {
      deleteChatHistory(session.sessionId);
    });
    
    console.log(`[Storage] Cleaned up ${toDelete.length} old sessions for ${sidebar}`);
  } catch (error) {
    console.error('[Storage] Failed to cleanup sessions:', error);
  }
}

/**
 * 获取当前边栏的最近会话（用于自动恢复）
 * @param {string} sidebar - 边栏类型
 * @returns {string|null} 最近会话ID
 */
export function getMostRecentSession(sidebar) {
  const sessions = getSessionsBySidebar(sidebar);
  return sessions.length > 0 ? sessions[0].sessionId : null;
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
