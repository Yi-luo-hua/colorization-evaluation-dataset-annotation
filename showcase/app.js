/**
 * 图像上色质量评估 (V4标准) · 典型成果展厅 核心逻辑
 */

// 内置完整备份数据 (支持直接双击 file:/// 打开而无需依赖 HTTP 服务器)
const EMBEDDED_SHOWCASE_DATA = [
  {
    "category_key": "pass",
    "category_title": "01_高保真放行 (0缺陷/Pass)",
    "task_id": 6887,
    "image_id": "lcad/000000396768.png",
    "basename": "000000396768.png",
    "image_stem": "000000396768",
    "gpt_score": 5.0,
    "original_gpt_score": 5.0,
    "reviewed_score": null,
    "review_status": "已核验",
    "review_note": "审查通过",
    "defects": [],
    "gt_relative_path": "images/000000396768_gt.jpg",
    "lcad_relative_path": "images/000000396768_lcad.png",
    "diff_relative_path": "images/000000396768_diff.png"
  },
  {
    "category_key": "A_missing",
    "category_title": "02_严重缺色 (熔断项 A)",
    "task_id": 6106,
    "image_id": "lcad/000000350748.png",
    "basename": "000000350748.png",
    "image_stem": "000000350748",
    "gpt_score": 1.0,
    "original_gpt_score": 1.0,
    "reviewed_score": 1.0,
    "review_status": "已核验",
    "review_note": "全图彻底上色失败，海滩沙滩、手抱冲浪板奔跑的冲浪者、海浪水花及背景天空均未渲染任何色彩，呈现彻底的纯灰阶黑白状态(A)。",
    "defects": [
      {
        "id": "A",
        "name": "缺色",
        "severity": "",
        "description": "全图彻底上色失败，海滩沙滩、手抱冲浪板奔跑的冲浪者、海浪水花及背景天空均未渲染任何色彩，呈现彻底的纯灰阶黑白状态(A)。"
      }
    ],
    "gt_relative_path": "images/000000350748_gt.jpg",
    "lcad_relative_path": "images/000000350748_lcad.png",
    "diff_relative_path": "images/000000350748_diff.png"
  },
  {
    "category_key": "C_wrong_color",
    "category_title": "03_常识错色 (严重错色 C-L3)",
    "task_id": 2973,
    "image_id": "lcad/000000172361.png",
    "basename": "000000172361.png",
    "image_stem": "000000172361",
    "gpt_score": 5.0,
    "original_gpt_score": 5.0,
    "reviewed_score": null,
    "review_status": "已核验",
    "review_note": "双层观光敞篷巴士醒目的鲜绿色下层车体被常识性严重错涂为亮橙黄色，公共交通标识色彩严重错配（严重常识错色 C-L3，轻度偏色 D-L1，视觉自然度受损 F-L2）。",
    "defects": [
      {
        "id": "C",
        "name": "错色",
        "severity": "L3",
        "description": "双层观光敞篷巴士醒目的鲜绿色下层车体被常识性严重错涂为亮橙黄色，公共交通标识色彩严重错配（严重常识错色 C-L3，轻度偏色 D-L1，视觉自然度受损 F-L2）。"
      },
      {
        "id": "D",
        "name": "偏色",
        "severity": "L1",
        "description": "双层观光敞篷巴士醒目的鲜绿色下层车体被常识性严重错涂为亮橙黄色，公共交通标识色彩严重错配（严重常识错色 C-L3，轻度偏色 D-L1，视觉自然度受损 F-L2）。"
      },
      {
        "id": "F",
        "name": "视觉自然度",
        "severity": "L2",
        "description": "双层观光敞篷巴士醒目的鲜绿色下层车体被常识性严重错涂为亮橙黄色，公共交通标识色彩严重错配（严重常识错色 C-L3，轻度偏色 D-L1，视觉自然度受损 F-L2）。"
      }
    ],
    "gt_relative_path": "images/000000172361_gt.jpg",
    "lcad_relative_path": "images/000000172361_lcad.png",
    "diff_relative_path": "images/000000172361_diff.png"
  },
  {
    "category_key": "B_bleed",
    "category_title": "04_边缘溢色 (轮廓扩散 B-L2)",
    "task_id": 6032,
    "image_id": "lcad/000000347121.png",
    "basename": "000000347121.png",
    "image_stem": "000000347121",
    "gpt_score": 1.01,
    "original_gpt_score": 1.01,
    "reviewed_score": null,
    "review_status": "已核验",
    "review_note": "庭院木栅栏与背景墙体颠覆性大面积错涂为极其刺目的亮天蓝色假色，且蓝色色料严重溢出侵染芭蕉树叶(B-L2, C-L3, D-L1, E1-L2, F-L3)。",
    "defects": [
      {
        "id": "B",
        "name": "溢色",
        "severity": "L2",
        "description": "庭院木栅栏与背景墙体颠覆性大面积错涂为极其刺目的亮天蓝色假色，且蓝色色料严重溢出侵染芭蕉树叶(B-L2, C-L3, D-L1, E1-L2, F-L3)。"
      },
      {
        "id": "C",
        "name": "错色",
        "severity": "L3",
        "description": "庭院木栅栏与背景墙体颠覆性大面积错涂为极其刺目的亮天蓝色假色，且蓝色色料严重溢出侵染芭蕉树叶(B-L2, C-L3, D-L1, E1-L2, F-L3)。"
      },
      {
        "id": "D",
        "name": "偏色",
        "severity": "L1",
        "description": "庭院木栅栏与背景墙体颠覆性大面积错涂为极其刺目的亮天蓝色假色，且蓝色色料严重溢出侵染芭蕉树叶(B-L2, C-L3, D-L1, E1-L2, F-L3)。"
      },
      {
        "id": "E1",
        "name": "过饱和",
        "severity": "L2",
        "description": "庭院木栅栏与背景墙体颠覆性大面积错涂为极其刺目的亮天蓝色假色，且蓝色色料严重溢出侵染芭蕉树叶(B-L2, C-L3, D-L1, E1-L2, F-L3)。"
      },
      {
        "id": "F",
        "name": "视觉自然度",
        "severity": "L3",
        "description": "庭院木栅栏与背景墙体颠覆性大面积错涂为极其刺目的亮天蓝色假色，且蓝色色料严重溢出侵染芭蕉树叶(B-L2, C-L3, D-L1, E1-L2, F-L3)。"
      }
    ],
    "gt_relative_path": "images/000000347121_gt.jpg",
    "lcad_relative_path": "images/000000347121_lcad.png",
    "diff_relative_path": "images/000000347121_diff.png"
  },
  {
    "category_key": "D_color_cast",
    "category_title": "05_系统性偏色 (色温偏差 D-L2)",
    "task_id": 6607,
    "image_id": "lcad/000000377983.png",
    "basename": "000000377983.png",
    "image_stem": "000000377983",
    "gpt_score": 2.47,
    "original_gpt_score": 2.47,
    "reviewed_score": null,
    "review_status": "已核验",
    "review_note": "人物面部和手臂肤色明显偏紫红，呈现不自然的冷色调偏移。；人物肤色与周围中性环境的色彩协调性稍差，轻微影响整体真实感。",
    "defects": [
      {
        "id": "D",
        "name": "偏色",
        "severity": "L2",
        "description": "人物面部和手臂肤色明显偏紫红，呈现不自然的冷色调偏移。"
      },
      {
        "id": "F",
        "name": "视觉自然度",
        "severity": "L1",
        "description": "人物肤色与周围中性环境的色彩协调性稍差，轻微影响整体真实感。"
      }
    ],
    "gt_relative_path": "images/000000377983_gt.jpg",
    "lcad_relative_path": "images/000000377983_lcad.png",
    "diff_relative_path": "images/000000377983_diff.png"
  },
  {
    "category_key": "E1_oversat",
    "category_title": "06_过饱和假色 (浓艳刺眼 E1-L2)",
    "task_id": 5871,
    "image_id": "lcad/000000338478.png",
    "basename": "000000338478.png",
    "image_stem": "000000338478",
    "gpt_score": 2.43,
    "original_gpt_score": 2.43,
    "reviewed_score": null,
    "review_status": "已核验",
    "review_note": "棒球场后方防护挡墙与草坪过饱和泛刺目电光青蓝假色(E1-L2, D-L1, F-L2)。",
    "defects": [
      {
        "id": "D",
        "name": "偏色",
        "severity": "L1",
        "description": "棒球场后方防护挡墙与草坪过饱和泛刺目电光青蓝假色(E1-L2, D-L1, F-L2)。"
      },
      {
        "id": "E1",
        "name": "过饱和",
        "severity": "L2",
        "description": "棒球场后方防护挡墙与草坪过饱和泛刺目电光青蓝假色(E1-L2, D-L1, F-L2)。"
      },
      {
        "id": "F",
        "name": "视觉自然度",
        "severity": "L2",
        "description": "棒球场后方防护挡墙与草坪过饱和泛刺目电光青蓝假色(E1-L2, D-L1, F-L2)。"
      }
    ],
    "gt_relative_path": "images/000000338478_gt.jpg",
    "lcad_relative_path": "images/000000338478_lcad.png",
    "diff_relative_path": "images/000000338478_diff.png"
  },
  {
    "category_key": "E2_undersat",
    "category_title": "07_严重欠饱和 (脱色泛灰 E2-L3)",
    "task_id": 9430,
    "image_id": "lcad/000000546864.png",
    "basename": "000000546864.png",
    "image_stem": "000000546864",
    "gpt_score": 1.02,
    "original_gpt_score": 1.02,
    "reviewed_score": null,
    "review_status": "已核验",
    "review_note": "棒球击球手黑白历史照片整幅画面大面积浸染暗灰红褐偏色，严重干瘪(D-L2, E2-L3, F-L2)。",
    "defects": [
      {
        "id": "D",
        "name": "偏色",
        "severity": "L2",
        "description": "棒球击球手历史黑白照片整幅画面大面积浸染暗灰红褐偏色。"
      },
      {
        "id": "E2",
        "name": "欠饱和",
        "severity": "L3",
        "description": "历史黑白照片全图严重欠饱和干瘪发灰。"
      },
      {
        "id": "F",
        "name": "视觉自然度",
        "severity": "L2",
        "description": "灰红褐色调覆盖使黑白人物照片浑浊不自然。"
      }
    ],
    "gt_relative_path": "images/000000546864_gt.jpg",
    "lcad_relative_path": "images/000000546864_lcad.png",
    "diff_relative_path": "images/000000546864_diff.png"
  },
  {
    "category_key": "F_naturalness",
    "category_title": "08_视觉自然度 (色斑违和 F-L2)",
    "task_id": 7803,
    "image_id": "lcad/000000448574.png",
    "basename": "000000448574.png",
    "image_stem": "000000448574",
    "gpt_score": 2.47,
    "original_gpt_score": 2.47,
    "reviewed_score": null,
    "review_status": "已核验",
    "review_note": "古典卧室木质四柱大床周围的暖黄光墙面与窗台大面积欠饱和褪色为阴冷死灰色，室内温馨氛围完全失真(D-L2, E2-L2, F-L2)。",
    "defects": [
      {
        "id": "D",
        "name": "偏色",
        "severity": "L2",
        "description": "古典卧室木质四柱大床周围的暖黄光墙面与窗台大面积欠饱和褪色为阴冷死灰色，室内温馨氛围完全失真(D-L2, E2-L2, F-L2)。"
      },
      {
        "id": "E2",
        "name": "欠饱和",
        "severity": "L2",
        "description": "古典卧室木质四柱大床周围的暖黄光墙面与窗台大面积欠饱和褪色为阴冷死灰色，室内温馨氛围完全失真(D-L2, E2-L2, F-L2)。"
      },
      {
        "id": "F",
        "name": "视觉自然度",
        "severity": "L2",
        "description": "古典卧室木质四柱大床周围的暖黄光墙面与窗台大面积欠饱和褪色为阴冷死灰色，室内温馨氛围完全失真(D-L2, E2-L2, F-L2)。"
      }
    ],
    "gt_relative_path": "images/000000448574_gt.jpg",
    "lcad_relative_path": "images/000000448574_lcad.png",
    "diff_relative_path": "images/000000448574_diff.png"
  },
  {
    "category_key": "multi_defects",
    "category_title": "09_复合多重受损 (多维缺陷并发)",
    "task_id": 3430,
    "image_id": "lcad/000000197624.png",
    "basename": "000000197624.png",
    "image_stem": "000000197624",
    "gpt_score": 2.73,
    "original_gpt_score": 2.73,
    "reviewed_score": null,
    "review_status": "已核验",
    "review_note": "浴室温馨暖黄瓷砖全图严重偏冷青蓝调完全失色褪为冰冷灰白水泥色(D-L2偏冷青蓝调, E2-L2, C-L1)。",
    "defects": [
      {
        "id": "C",
        "name": "错色",
        "severity": "L1",
        "description": "温馨暖黄瓷砖浴室采光氛围被彻底剥夺"
      },
      {
        "id": "D",
        "name": "偏色",
        "severity": "L2",
        "description": "全图严重偏冷青蓝调，完全失色退化为冰冷灰白水泥色"
      },
      {
        "id": "E2",
        "name": "欠饱和",
        "severity": "L2",
        "description": "墙面与陶瓷严重欠饱和"
      }
    ],
    "gt_relative_path": "images/000000197624_gt.jpg",
    "lcad_relative_path": "images/000000197624_lcad.png",
    "diff_relative_path": "images/000000197624_diff.png"
  },
  {
    "category_key": "fine_grounding",
    "category_title": "10_精细具象定物 (消灭抽象代词)",
    "task_id": 5895,
    "image_id": "lcad/000000340354.png",
    "basename": "000000340354.png",
    "image_stem": "000000340354",
    "gpt_score": 4.23,
    "original_gpt_score": 4.23,
    "reviewed_score": null,
    "review_status": "已核验",
    "review_note": "沙滩上空翱翔的菱形风筝原本极度醒目的鲜艳明黄色颠覆性彻底脱色错涂为苍白水冷青灰(C-L3, E2-L3, F-L2)。",
    "defects": [
      {
        "id": "C",
        "name": "错色",
        "severity": "L3",
        "description": "沙滩上空翱翔的菱形风筝原本极度醒目的鲜艳明黄色颠覆性彻底脱色错涂为苍白水冷青灰(C-L3, E2-L3, F-L2)。"
      },
      {
        "id": "E2",
        "name": "欠饱和",
        "severity": "L3",
        "description": "沙滩上空翱翔的菱形风筝原本极度醒目的鲜艳明黄色颠覆性彻底脱色错涂为苍白水冷青灰(C-L3, E2-L3, F-L2)。"
      },
      {
        "id": "F",
        "name": "视觉自然度",
        "severity": "L2",
        "description": "沙滩上空翱翔的菱形风筝原本极度醒目的鲜艳明黄色颠覆性彻底脱色错涂为苍白水冷青灰(C-L3, E2-L3, F-L2)。"
      }
    ],
    "gt_relative_path": "images/000000340354_gt.jpg",
    "lcad_relative_path": "images/000000340354_lcad.png",
    "diff_relative_path": "images/000000340354_diff.png"
  }
];

let currentCases = [];
let activeFilter = 'all';
let currentViewMode = 'triptych'; // 'triptych' | 'slider' | 'diff-only'

document.addEventListener('DOMContentLoaded', async () => {
  await initShowcaseData();
  bindGlobalEvents();
  renderCards();
});

async function initShowcaseData() {
  try {
    const res = await fetch('showcase_data.json');
    if (res.ok) {
      currentCases = await res.json();
    } else {
      currentCases = EMBEDDED_SHOWCASE_DATA;
    }
  } catch (e) {
    // file:/// 跨域时自动回退到内嵌数据
    console.warn('使用内置数据渲染展厅:', e);
    currentCases = EMBEDDED_SHOWCASE_DATA;
  }
}

function bindGlobalEvents() {
  // 分类筛选
  const filterBtns = document.querySelectorAll('.filter-btn');
  filterBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      filterBtns.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      activeFilter = btn.dataset.filter;
      renderCards();
    });
  });

  // 视图模式切换
  const viewBtns = document.querySelectorAll('.view-btn');
  viewBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      viewBtns.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      currentViewMode = btn.dataset.view;
      renderCards();
    });
  });

  // Lightbox 关闭
  const lightbox = document.getElementById('lightbox');
  const closeBtn = document.getElementById('lightbox-close');
  const backdrop = document.getElementById('lightbox-backdrop');

  const closeLightbox = () => lightbox.classList.remove('active');
  closeBtn.addEventListener('click', closeLightbox);
  backdrop.addEventListener('click', closeLightbox);
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') closeLightbox();
  });
}

function getDefectClass(id) {
  const map = {
    'A': 'def-a',
    'B': 'def-b',
    'C': 'def-c',
    'D': 'def-d',
    'E1': 'def-e1',
    'E2': 'def-e2',
    'F': 'def-f'
  };
  return map[id] || '';
}

function renderCards() {
  const container = document.getElementById('cards-container');
  if (!container) return;

  const filtered = currentCases.filter(item => {
    if (activeFilter === 'all') return true;
    if (activeFilter === 'pass') return item.defects.length === 0;
    if (activeFilter === 'severe') {
      return item.defects.some(d => d.id === 'A' || (d.id === 'C' && d.severity === 'L3'));
    }
    if (activeFilter === 'color') {
      return item.defects.some(d => d.id === 'C' || d.id === 'D');
    }
    if (activeFilter === 'grounding') {
      return item.category_key === 'fine_grounding' || item.defects.length >= 2;
    }
    return true;
  });

  container.innerHTML = filtered.map((item, index) => createCardHTML(item, index)).join('');

  // 绑定图片放大查看事件
  container.querySelectorAll('.zoomable-img').forEach(img => {
    img.addEventListener('click', () => {
      openLightbox(img.src, img.dataset.caption || '细节查看', img.dataset.subcaption || '');
    });
  });

  // 如果处于卷帘对比模式，初始化滑块交互
  if (currentViewMode === 'slider') {
    initSliders();
  }
}

function createCardHTML(item, displayIndex) {
  const isPass = item.defects.length === 0;
  const isMeltdown = item.defects.some(d => d.id === 'A');

  // 打分展示
  let scoreClass = 'highlight';
  let scoreText = item.gpt_score !== null ? item.gpt_score.toFixed(2) : '-';
  if (isPass) {
    scoreClass = 'pass';
  } else if (isMeltdown) {
    scoreClass = 'meltdown';
    scoreText = '1.00 (熔断)';
  }

  // 缺陷徽章
  let badgesHTML = '';
  if (isPass) {
    badgesHTML = '<span class="defect-pill pass">🟢 0 缺陷 · 高保真放行</span>';
  } else {
    badgesHTML = item.defects.map(d => {
      const cls = getDefectClass(d.id);
      const sev = d.severity ? `<span class="severity-tag">${d.severity}</span>` : '';
      return `<span class="defect-pill ${cls}">${d.id} ${d.name} ${sev}</span>`;
    }).join('');
  }

  // 媒体展示区（根据 currentViewMode 决定）
  let mediaHTML = '';
  if (currentViewMode === 'triptych') {
    mediaHTML = `
      <div class="view-triptych-grid">
        <div class="img-slot">
          <div class="img-slot-header">
            <span class="img-slot-label"><span class="indicator-dot dot-gt"></span>真值彩色图 (Ground Truth)</span>
            <span class="task-meta-tag">GT 真实色彩</span>
          </div>
          <div class="img-wrapper">
            <img class="zoomable-img" src="${item.gt_relative_path}" data-caption="${item.category_title} · GT 彩色真值图" data-subcaption="图像编号: ${item.image_id}" alt="GT 真值图">
            <span class="img-zoom-hint">🔍 点击全屏</span>
          </div>
        </div>

        <div class="img-slot">
          <div class="img-slot-header">
            <span class="img-slot-label"><span class="indicator-dot dot-lcad"></span>LCAD 模型上色 (Colorized)</span>
            <span class="task-meta-tag">生成模型表现</span>
          </div>
          <div class="img-wrapper">
            <img class="zoomable-img" src="${item.lcad_relative_path}" data-caption="${item.category_title} · LCAD 模型上色图" data-subcaption="图像编号: ${item.image_id}" alt="LCAD 生成图">
            <span class="img-zoom-hint">🔍 点击全屏</span>
          </div>
        </div>

        <div class="img-slot">
          <div class="img-slot-header">
            <span class="img-slot-label"><span class="indicator-dot dot-diff"></span>2x 增强差分热力图 (Diff)</span>
            <span class="task-meta-tag">高亮区域代表失真</span>
          </div>
          <div class="img-wrapper">
            <img class="zoomable-img" src="${item.diff_relative_path}" data-caption="${item.category_title} · 2x 差分失真热力图" data-subcaption="亮斑区域即颜色偏差集中处" alt="2x 差分图">
            <span class="img-zoom-hint">🔍 点击全屏</span>
          </div>
        </div>
      </div>
    `;
  } else if (currentViewMode === 'slider') {
    mediaHTML = `
      <div class="view-slider-wrapper" id="slider-${item.task_id}">
        <span class="slider-badge left">左侧：彩色真值 (GT)</span>
        <span class="slider-badge right">右侧：LCAD 上色</span>
        <img class="slider-img lcad" src="${item.lcad_relative_path}" alt="LCAD">
        <div class="slider-clipped-wrap">
          <img class="slider-img gt" src="${item.gt_relative_path}" alt="GT">
        </div>
        <div class="slider-handle">
          <div class="slider-button">↔</div>
        </div>
      </div>
    `;
  } else {
    // 差分透视
    mediaHTML = `
      <div class="view-diff-only-wrap">
        <img class="zoomable-img" src="${item.diff_relative_path}" data-caption="${item.category_title} · 2x 差分失真热力图" data-subcaption="高亮光斑精确指示受损部位" alt="差分热力图">
      </div>
    `;
  }

  // 定物描述高亮处理
  let groundingHTML = '';
  if (isPass) {
    groundingHTML = `
      <div class="grounding-box pass-box">
        <div class="grounding-header">
          <span class="grounding-title">🟢 双重硬门槛核验放行结论</span>
          <span class="task-meta-tag">ΔC &lt; 0.08 · 2x差分几近全黑</span>
        </div>
        <div class="grounding-content">
          该样本经 2x 增强差分热力图与彩色真值大图严谨复核，关键物体色彩过渡自然，光影与材质完全契合真值标准，各项指标自洽且无任何色温漂移或边缘溢色，判定为<strong>审查通过放行 (0 缺陷)</strong>。
        </div>
      </div>
    `;
  } else {
    const boxCls = isMeltdown ? 'meltdown-box' : '';
    const noteText = item.review_note || (item.defects.length ? item.defects[0].description : '');

    // 细项描述列表
    const defectItemsListHTML = item.defects.map(d => {
      const cls = getDefectClass(d.id);
      return `
        <div class="defect-single-item">
          <span class="defect-single-label ${cls}">[${d.id} ${d.name} ${d.severity || ''}]</span>
          <span class="defect-single-desc">${d.description}</span>
        </div>
      `;
    }).join('');

    groundingHTML = `
      <div class="grounding-box ${boxCls}">
        <div class="grounding-header">
          <span class="grounding-title">🎯 具象实体定物审校结论 (Grounding Annotation)</span>
          <span class="task-meta-tag">消灭抽象代词 · 精准定位物体</span>
        </div>
        <div class="grounding-content">
          ${noteText}
        </div>
        <div class="defect-items-list">
          ${defectItemsListHTML}
        </div>
      </div>
    `;
  }

  return `
    <article class="case-card" id="task-${item.task_id}">
      <div class="case-card-header">
        <div class="card-title-group">
          <span class="case-badge-index">CASE ${String(displayIndex + 1).padStart(2, '0')}</span>
          <div>
            <h2 class="case-title">${item.category_title}</h2>
            <span class="task-meta-tag">Task #${item.task_id} · ${item.image_id}</span>
          </div>
        </div>

        <div class="card-score-group">
          <div class="score-item">
            <span class="score-title">评测打分</span>
            <span class="score-val ${scoreClass}">${scoreText}</span>
          </div>
          <div class="score-item">
            <span class="score-title">质检状态</span>
            <span class="score-val" style="color: #a5b4fc;">100% 已核验</span>
          </div>
        </div>
      </div>

      <div class="card-media-area">
        ${mediaHTML}
      </div>

      <div class="card-details">
        <div class="defect-badges-container">
          <span class="toggle-label">缺陷判定：</span>
          ${badgesHTML}
        </div>
        ${groundingHTML}
      </div>
    </article>
  `;
}

function openLightbox(src, title, subtitle) {
  const lightbox = document.getElementById('lightbox');
  const img = document.getElementById('lightbox-img');
  const titleEl = document.getElementById('lightbox-title');
  const subEl = document.getElementById('lightbox-subtitle');

  img.src = src;
  titleEl.textContent = title;
  subEl.textContent = subtitle;
  lightbox.classList.add('active');
}

function initSliders() {
  const sliderWrappers = document.querySelectorAll('.view-slider-wrapper');
  sliderWrappers.forEach(slider => {
    const clippedWrap = slider.querySelector('.slider-clipped-wrap');
    const handle = slider.querySelector('.slider-handle');

    let isDown = false;

    const setSliderPos = (clientX) => {
      const rect = slider.getBoundingClientRect();
      let x = clientX - rect.left;
      if (x < 0) x = 0;
      if (x > rect.width) x = rect.width;
      const percent = (x / rect.width) * 100;

      clippedWrap.style.clipPath = `polygon(0 0, ${percent}% 0, ${percent}% 100%, 0 100%)`;
      handle.style.left = `${percent}%`;
    };

    slider.addEventListener('mousedown', (e) => {
      isDown = true;
      setSliderPos(e.clientX);
    });

    window.addEventListener('mouseup', () => {
      isDown = false;
    });

    slider.addEventListener('mousemove', (e) => {
      if (!isDown) return;
      setSliderPos(e.clientX);
    });

    // 触摸支持
    slider.addEventListener('touchstart', (e) => {
      isDown = true;
      setSliderPos(e.touches[0].clientX);
    }, { passive: true });

    slider.addEventListener('touchmove', (e) => {
      if (!isDown) return;
      setSliderPos(e.touches[0].clientX);
    }, { passive: true });

    slider.addEventListener('touchend', () => {
      isDown = false;
    });
  });
}
