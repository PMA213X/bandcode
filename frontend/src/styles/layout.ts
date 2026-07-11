/**
 * layout.ts - 布局样式定义
 */

/**
 * 间距常量
 */
export const SPACING = {
  xs: 1,
  sm: 2,
  md: 3,
  lg: 4,
  xl: 5,
};

/**
 * 边框样式
 */
export const BORDERS = {
  single: "single",
  double: "double",
  round: "round",
  bold: "bold",
  none: "none",
};

/**
 * 对齐方式
 */
export const ALIGNMENT = {
  left: "left",
  center: "center",
  right: "right",
};

/**
 * 布局预设
 */
export const LAYOUTS = {
  // 消息气泡
  messageBubble: {
    paddingX: SPACING.sm,
    marginBottom: SPACING.xs,
  },

  // 输入框
  inputBox: {
    paddingX: SPACING.sm,
    paddingY: SPACING.xs,
    borderStyle: BORDERS.single,
  },

  // 面板
  panel: {
    padding: SPACING.sm,
    borderStyle: BORDERS.single,
  },

  // 列表项
  listItem: {
    paddingX: SPACING.sm,
    paddingY: SPACING.xs,
  },

  // 标题
  title: {
    marginBottom: SPACING.sm,
  },

  // 分隔线
  separator: {
    marginY: SPACING.xs,
  },
};