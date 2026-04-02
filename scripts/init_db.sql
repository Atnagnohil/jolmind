-- ==============================
-- 用户表（扩展多用户用）
-- ==============================
DROP TABLE IF EXISTS user;
CREATE TABLE user
(
    id          BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '用户主键ID',
    avatar      VARCHAR(255)    NOT NULL DEFAULT '' COMMENT '用户头像URL',
    nickname    VARCHAR(64)     NOT NULL DEFAULT '' COMMENT '用户昵称',
    create_time DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    update_time DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (id)
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4 COMMENT ='用户表';

-- 创建单用户
INSERT INTO user (id, nickname)
VALUES (1, 'master');

-- ==============================
-- 会话表
-- ==============================
DROP TABLE IF EXISTS chat_session;
CREATE TABLE chat_session
(
    id             CHAR(36)         NOT NULL COMMENT '会话主键ID（UUID）',
    user_id        BIGINT UNSIGNED  NOT NULL COMMENT '关联用户ID',
    session_name   VARCHAR(64)      NOT NULL DEFAULT '新会话' COMMENT '会话名称',
    session_status TINYINT UNSIGNED NOT NULL DEFAULT 1 COMMENT '会话状态 0-关闭 1-进行中',
    remark         VARCHAR(255)     NOT NULL DEFAULT '' COMMENT '会话备注',
    create_time    DATETIME         NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    update_time    DATETIME         NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    is_deleted     TINYINT UNSIGNED NOT NULL DEFAULT 0 COMMENT '逻辑删除 0-未删除 1-已删除',
    PRIMARY KEY (id),
    KEY idx_user_id (user_id) COMMENT '用户ID索引'
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4 COMMENT ='对话会话表';

-- ==============================
-- 工具调用日志表（日志表）
-- ==============================
DROP TABLE IF EXISTS tool_call_log;
CREATE TABLE tool_call_log
(
    id          BIGINT UNSIGNED  NOT NULL AUTO_INCREMENT COMMENT '日志主键ID',
    user_id     BIGINT UNSIGNED  NOT NULL COMMENT '操作用户ID',
    session_id  CHAR(36)         NOT NULL COMMENT '关联会话ID',
    tool_name   VARCHAR(64)      NOT NULL COMMENT '工具名称',
    call_params JSON COMMENT '调用入参（JSON格式）',
    call_result JSON COMMENT '调用返回结果（JSON格式）',
    call_status TINYINT UNSIGNED NOT NULL DEFAULT 1 COMMENT '调用状态 0-失败 1-成功',
    cost_time   INT UNSIGNED     NOT NULL DEFAULT 0 COMMENT '调用耗时（毫秒）',
    error_msg   VARCHAR(512)     NOT NULL DEFAULT '' COMMENT '失败错误信息',
    create_time DATETIME         NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    update_time DATETIME         NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    is_deleted  TINYINT UNSIGNED NOT NULL DEFAULT 0 COMMENT '逻辑删除 0-未删除 1-已删除',
    PRIMARY KEY (id),
    KEY idx_user_id (user_id) COMMENT '用户ID索引',
    KEY idx_session_id (session_id) COMMENT '会话ID索引',
    KEY idx_tool_name (tool_name) COMMENT '工具名称索引'
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4 COMMENT ='工具调用日志表';

-- ==============================
-- 消息表
-- ==============================
DROP TABLE IF EXISTS chat_message;
CREATE TABLE chat_message
(
    id           BIGINT UNSIGNED  NOT NULL AUTO_INCREMENT COMMENT '消息主键ID',
    user_id      BIGINT UNSIGNED  NOT NULL COMMENT '关联用户ID',
    session_id   CHAR(36)         NOT NULL COMMENT '关联会话ID',
    role         TINYINT UNSIGNED NOT NULL COMMENT '消息角色 0-user 1-assistant 2-tool',
    content      TEXT             NOT NULL COMMENT '消息内容',
    tool_call_id BIGINT UNSIGNED           DEFAULT NULL COMMENT '关联工具调用日志ID（role=tool时有值）',
    token_count  INT UNSIGNED     NOT NULL DEFAULT 0 COMMENT '消息token数',
    create_time  DATETIME         NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    update_time  DATETIME         NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    is_deleted   TINYINT UNSIGNED NOT NULL DEFAULT 0 COMMENT '逻辑删除 0-未删除 1-已删除',
    PRIMARY KEY (id),
    KEY idx_session_id (session_id) COMMENT '会话ID索引',
    KEY idx_user_id (user_id) COMMENT '用户ID索引'
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4 COMMENT ='对话消息表';
