/**
 * Notion 风格 · Ant Design v5 主题配置
 * 云志选专属，2026
 */
const notionTheme = {
  token: {
    // ─── Notion 色板 ───
    colorPrimary: '#2F8CFF',
    colorSuccess: '#3CB371',
    colorWarning: '#E8A838',
    colorError: '#E25C5C',
    colorInfo: '#2F8CFF',

    colorBgLayout: '#F7F6F3',
    colorBgContainer: '#FFFFFF',
    colorBgElevated: '#FFFFFF',
    colorBgSpotlight: '#F1F0EB',

    colorText: '#37352F',
    colorTextSecondary: '#9B9A97',
    colorTextTertiary: '#B4B4B0',
    colorTextQuaternary: '#D0CFCC',

    colorBorder: '#EBE9E4',
    colorBorderSecondary: '#EBE9E4',

    colorFillTertiary: '#F1F0EB',
    colorFillQuaternary: '#F1F0EB',

    // ─── 排版 ───
    fontFamily: "-apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, 'Apple Color Emoji', Arial, sans-serif",
    fontSize: 14,
    fontSizeHeading1: 28,
    fontSizeHeading2: 20,
    fontSizeHeading3: 16,
    fontSizeHeading4: 14,
    fontSizeHeading5: 14,

    // ─── 圆角 ───
    borderRadius: 4,
    borderRadiusSM: 3,
    borderRadiusLG: 6,

    // ─── 间距 ───
    padding: 16,
    paddingLG: 20,
    paddingSM: 12,
    paddingXS: 8,
    margin: 16,
    marginLG: 20,
    marginSM: 12,
    marginXS: 8,

    // ─── 阴影（Notion 风格极轻）───
    boxShadow: '0 1px 2px rgba(0,0,0,0.04)',
    boxShadowSecondary: '0 1px 3px rgba(0,0,0,0.06)',
  },

  components: {
    Layout: {
      headerBg: '#FFFFFF',
      headerColor: '#37352F',
      headerPadding: '0 24px',
      bodyBg: '#F7F6F3',
      footerBg: '#F7F6F3',
    },
    Card: {
      colorBgContainer: '#FFFFFF',
      borderRadiusLG: 4,
      padding: 16,
      boxShadow: 'none',
      boxShadowTertiary: 'none',
    },
    Button: {
      primaryColor: '#FFFFFF',
      defaultBorderColor: '#EBE9E4',
      defaultBg: '#FFFFFF',
      defaultColor: '#37352F',
      borderRadius: 4,
      borderRadiusSM: 3,
      borderRadiusLG: 4,
    },
    Table: {
      headerBg: '#F7F6F3',
      headerColor: '#B4B4B0',
      headerBorderRadius: 0,
      rowHoverBg: '#F1F0EB',
      borderColor: '#EBE9E4',
    },
    Menu: {
      itemBg: 'transparent',
      itemColor: '#37352F',
      itemHoverColor: '#37352F',
      itemHoverBg: '#EBE9E4',
      itemSelectedColor: '#2F8CFF',
      itemSelectedBg: '#E8F0FE',
      subMenuItemBg: 'transparent',
      collapsedIconColor: '#9B9A97',
    },
    Tabs: {
      inkBarColor: '#37352F',
      itemColor: '#9B9A97',
      itemSelectedColor: '#37352F',
      itemHoverColor: '#37352F',
    },
    Input: {
      colorBgContainer: '#F7F6F3',
      colorBorder: '#EBE9E4',
      activeBorderColor: '#2F8CFF',
      activeShadow: '0 0 0 2px rgba(47,140,255,0.1)',
      borderRadius: 4,
    },
    Select: {
      colorBgContainer: '#FFFFFF',
      colorBorder: '#EBE9E4',
      optionSelectedBg: '#E8F0FE',
    },
    Modal: {
      contentBg: '#FFFFFF',
      headerBg: '#FFFFFF',
      footerBg: '#FFFFFF',
    },
    Tag: {
      defaultBg: '#EBE9E4',
      defaultColor: '#9B9A97',
    },
    Steps: {
      navArrowColor: '#EBE9E4',
      descriptionMaxWidth: 200,
      customIconSize: 32,
      iconSize: 32,
      iconFontSize: 14,
      finishIconBorderColor: '#3CB371',
      finishIconBg: '#E6F7EC',
    },
    Progress: {
      defaultColor: '#2F8CFF',
      remainingColor: '#EBE9E4',
      borderRadius: 3,
    },
    Drawer: {
      colorBgElevated: '#FFFFFF',
    },
  },
};

export default notionTheme;
