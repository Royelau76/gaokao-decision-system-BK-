import React, { useState } from 'react';
import { Table, Tag, Button, Card, Progress, Row, Col, Drawer, Descriptions, Badge, Space, Tooltip } from 'antd';

const SEVERITY_COLOR = { high: 'error', mid: 'warning', low: 'default' };
const SEVERITY_LABEL = { high: '高', mid: '中', low: '低' };
const CONFIDENCE_LABEL = { L1: '官方', L2: '行业', L3: '估算' };
const CONFIDENCE_COLOR = { L1: 'green', L2: 'blue', L3: 'default' };

const RecommendationList = ({ recommendations, onGenerateVolunteerTable }) => {
  const [drawerRec, setDrawerRec] = useState(null);

  const columns = [
    {
      title: '梯度',
      dataIndex: 'level',
      key: 'level',
      width: 70,
      render: (level) => {
        const colorMap = { '冲': 'red', '稳': 'blue', '保': 'green' };
        return <Tag color={colorMap[level]}>{level}</Tag>;
      },
    },
    {
      title: '院校 / 专业',
      key: 'uni_major',
      render: (_, r) => (
        <div>
          <div style={{ fontWeight: 500 }}>
            {r.university_name}
            {(r.tags || []).filter(t => t.type === 'level').map(t => (
              <Tag key={t.value} color="purple" style={{ marginLeft: 6 }}>{t.value}</Tag>
            ))}
          </div>
          <div style={{ color: '#9B9A97', fontSize: 12, marginTop: 2 }}>{r.major}</div>
        </div>
      ),
    },
    {
      title: '位次',
      key: 'rank_history',
      width: 160,
      render: (_, r) => {
        const history = r.min_rank_history || {};
        const years = Object.keys(history).sort();
        if (years.length === 0) {
          return r.min_rank ? r.min_rank.toLocaleString() : '—';
        }
        if (years.length === 1) {
          const y = years[0];
          return (
            <Tooltip title={`仅 ${y} 年单年数据`}>
              <span>
                {history[y].toLocaleString()}
                <Tag color="default" style={{ marginLeft: 4, fontSize: 10, padding: '0 4px' }}>{y}</Tag>
              </span>
            </Tooltip>
          );
        }
        const trend = years.map(y => history[y]);
        // 数字变小=门槛升高(对考生不利,红色↑)，数字变大=门槛降低(对考生有利,绿色↓)
        const last = trend[trend.length - 1];
        const first = trend[0];
        const arrow = last < first ? '↑' : last > first ? '↓' : '→';
        const arrowColor = arrow === '↑' ? '#ff4d4f' : arrow === '↓' ? '#52c41a' : '#9B9A97';
        return (
          <Tooltip title={years.map(y => `${y}年 ${history[y].toLocaleString()}名`).join(' / ')}>
            <span style={{ fontSize: 12 }}>
              {trend.map((v, i) => (
                <span key={i}>
                  {v.toLocaleString()}
                  {i < trend.length - 1 && <span style={{ color: arrowColor, margin: '0 4px' }}>{arrow}</span>}
                </span>
              ))}
            </span>
          </Tooltip>
        );
      },
    },
    {
      title: '就业率',
      key: 'employment_rate',
      width: 110,
      render: (_, r) => {
        const emp = r.employment;
        if (!emp || emp.employment_rate == null) return <span style={{ color: '#B4B4B0' }}>—</span>;
        const conf = emp.employment_rate_official ? 'L1' : 'L2';
        return (
          <Tooltip title={emp.employment_rate_definition || (emp.employment_rate_official ? '学校官方发布' : '行业统计')}>
            <span>
              {emp.employment_rate}%
              <Tag color={CONFIDENCE_COLOR[conf]} style={{ marginLeft: 4, fontSize: 10, padding: '0 4px' }}>
                {CONFIDENCE_LABEL[conf]}
              </Tag>
            </span>
          </Tooltip>
        );
      },
    },
    {
      title: '月薪区间',
      key: 'salary_range',
      width: 150,
      render: (_, r) => {
        const emp = r.employment;
        if (!emp || !emp.salary_range) return <span style={{ color: '#B4B4B0' }}>—</span>;
        const conf = emp.salary_estimated ? 'L3' : 'L1';
        return (
          <Tooltip title={emp.salary_source || ''}>
            <span>
              {emp.salary_range}
              <Tag color={CONFIDENCE_COLOR[conf]} style={{ marginLeft: 4, fontSize: 10, padding: '0 4px' }}>
                {CONFIDENCE_LABEL[conf]}
              </Tag>
            </span>
          </Tooltip>
        );
      },
    },
    {
      title: '风险',
      key: 'risks',
      width: 120,
      render: (_, r) => {
        const risks = r.risks || [];
        if (risks.length === 0) return <span style={{ color: '#9B9A97' }}>无</span>;
        const high = risks.filter(x => x.severity === 'high').length;
        const mid = risks.filter(x => x.severity === 'mid').length;
        const low = risks.filter(x => x.severity === 'low').length;
        return (
          <Space size={4}>
            {high > 0 && <Badge count={high} style={{ backgroundColor: '#ff4d4f' }} />}
            {mid > 0 && <Badge count={mid} style={{ backgroundColor: '#faad14' }} />}
            {low > 0 && <Badge count={low} style={{ backgroundColor: '#d9d9d9', color: '#595959' }} />}
          </Space>
        );
      },
    },
    {
      title: '录取概率',
      dataIndex: 'admission_probability',
      key: 'probability',
      width: 130,
      render: (prob) => (
        <Progress
          percent={prob}
          size="small"
          status={prob > 70 ? 'success' : prob > 40 ? 'normal' : 'exception'}
        />
      ),
    },
    {
      title: '综合评分',
      dataIndex: 'composite_score',
      key: 'composite_score',
      width: 100,
      sorter: (a, b) => (a.composite_score || 0) - (b.composite_score || 0),
      render: (score) => (
        <span style={{
          fontWeight: 600,
          color: score >= 60 ? '#3CB371' : score >= 40 ? '#E8A838' : '#9B9A97',
        }}>
          {score != null ? score.toFixed(1) : '—'}
        </span>
      ),
    },
  ];

  const 冲数量 = recommendations.filter(r => r.level === '冲').length;
  const 稳数量 = recommendations.filter(r => r.level === '稳').length;
  const 保数量 = recommendations.filter(r => r.level === '保').length;
  const 高风险数 = recommendations.filter(r => (r.risks || []).some(x => x.severity === 'high')).length;

  return (
    <div>
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col xs={12} sm={6}>
          <Card>
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: 28, color: '#ff4d4f', fontWeight: 'bold' }}>{冲数量}</div>
              <div style={{ fontSize: 13 }}>冲刺院校</div>
            </div>
          </Card>
        </Col>
        <Col xs={12} sm={6}>
          <Card>
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: 28, color: '#1890ff', fontWeight: 'bold' }}>{稳数量}</div>
              <div style={{ fontSize: 13 }}>稳妥院校</div>
            </div>
          </Card>
        </Col>
        <Col xs={12} sm={6}>
          <Card>
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: 28, color: '#52c41a', fontWeight: 'bold' }}>{保数量}</div>
              <div style={{ fontSize: 13 }}>保底院校</div>
            </div>
          </Card>
        </Col>
        <Col xs={12} sm={6}>
          <Card>
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: 28, color: '#faad14', fontWeight: 'bold' }}>{高风险数}</div>
              <div style={{ fontSize: 13 }}>含高风险</div>
            </div>
          </Card>
        </Col>
      </Row>

      <Table
        dataSource={recommendations}
        columns={columns}
        rowKey="suggested_order"
        pagination={{ pageSize: 10 }}
        scroll={{ x: 1100 }}
        onRow={(record) => ({
          onClick: () => setDrawerRec(record),
          style: { cursor: 'pointer' },
        })}
      />

      <Button
        type="primary"
        size="large"
        block
        style={{ marginTop: 24 }}
        onClick={onGenerateVolunteerTable}
      >
        生成志愿方案表
      </Button>

      <Drawer
        title={drawerRec ? `${drawerRec.university_name} · ${drawerRec.major}` : ''}
        open={!!drawerRec}
        onClose={() => setDrawerRec(null)}
        width={560}
      >
        {drawerRec && <RecDetail rec={drawerRec} />}
      </Drawer>
    </div>
  );
};

const RecDetail = ({ rec }) => {
  const emp = rec.employment;
  const risks = rec.risks || [];
  const tags = rec.tags || [];

  return (
    <>
      <Descriptions column={1} size="small" bordered style={{ marginBottom: 16 }}>
        <Descriptions.Item label="梯度">
          <Tag color={{ 冲: 'red', 稳: 'blue', 保: 'green' }[rec.level]}>{rec.level}</Tag>
          <span style={{ marginLeft: 8 }}>录取概率 {rec.admission_probability}%</span>
          <span style={{ marginLeft: 12, color: '#9B9A97' }}>综合评分 {rec.composite_score}</span>
        </Descriptions.Item>
        <Descriptions.Item label="院校层次">
          {tags.length > 0
            ? tags.map(t => <Tag key={`${t.type}-${t.value}`} color="purple">{t.value}</Tag>)
            : <span style={{ color: '#9B9A97' }}>无</span>}
        </Descriptions.Item>
        <Descriptions.Item label="位次范围">
          {(() => {
            const history = rec.min_rank_history || {};
            const years = Object.keys(history).sort();
            if (years.length === 0) return rec.min_rank ? rec.min_rank.toLocaleString() : '—';
            return (
              <span>
                {years.map(y => (
                  <span key={y} style={{ marginRight: 12 }}>
                    {y}年 <strong>{history[y].toLocaleString()}</strong>
                  </span>
                ))}
                {years.length > 1 && (
                  <span style={{ color: '#9B9A97', fontSize: 12, marginLeft: 8 }}>
                    平均 {rec.min_rank.toLocaleString()} · 跨度 {rec.volatility} 名
                  </span>
                )}
              </span>
            );
          })()}
        </Descriptions.Item>
      </Descriptions>

      <Card size="small" title="就业产出" style={{ marginBottom: 16 }}>
        {emp ? (
          <Descriptions column={1} size="small">
            <Descriptions.Item label="就业率">
              {emp.employment_rate != null ? `${emp.employment_rate}%` : '—'}
              {emp.employment_rate_official != null && (
                <Tag color={CONFIDENCE_COLOR[emp.employment_rate_official ? 'L1' : 'L2']} style={{ marginLeft: 6 }}>
                  {emp.employment_rate_official ? '学校官方' : '行业统计'}
                </Tag>
              )}
              {emp.employment_rate_definition && (
                <div style={{ color: '#9B9A97', fontSize: 12, marginTop: 2 }}>口径：{emp.employment_rate_definition}</div>
              )}
            </Descriptions.Item>
            <Descriptions.Item label="月薪区间">
              {emp.salary_range || '—'}
              {emp.salary_range && (
                <Tag color={CONFIDENCE_COLOR[emp.salary_estimated ? 'L3' : 'L1']} style={{ marginLeft: 6 }}>
                  {emp.salary_estimated ? '行业估算' : '学校官方'}
                </Tag>
              )}
              {emp.salary_source && (
                <div style={{ color: '#9B9A97', fontSize: 12, marginTop: 2 }}>来源：{emp.salary_source}</div>
              )}
            </Descriptions.Item>
            <Descriptions.Item label="深造率">
              {emp.grad_rate != null ? `${emp.grad_rate}%` : '—'}
              {emp.grad_rate != null && emp.grad_rate_official != null && (
                <Tag color={CONFIDENCE_COLOR[emp.grad_rate_official ? 'L1' : 'L2']} style={{ marginLeft: 6 }}>
                  {emp.grad_rate_official ? '学校官方' : '行业统计'}
                </Tag>
              )}
              {emp.grad_rate_note && (
                <div style={{ color: '#9B9A97', fontSize: 12, marginTop: 2 }}>口径：{emp.grad_rate_note}</div>
              )}
            </Descriptions.Item>
            <Descriptions.Item label="主要去向">
              {(emp.top_employers || []).length > 0
                ? (emp.top_employers || []).map(e => <Tag key={e}>{e}</Tag>)
                : <span style={{ color: '#9B9A97' }}>—</span>}
            </Descriptions.Item>
            <Descriptions.Item label="方向标签">
              {(emp.direction_tags || []).length > 0
                ? (emp.direction_tags || []).map(t => <Tag key={t} color="cyan">{t}</Tag>)
                : <span style={{ color: '#9B9A97' }}>—</span>}
            </Descriptions.Item>
          </Descriptions>
        ) : (
          <div style={{ color: '#9B9A97' }}>暂无该专业大类的就业产出数据</div>
        )}
      </Card>

      <Card size="small" title={`风险提示（${risks.length}）`} style={{ marginBottom: 16 }}>
        {risks.length === 0 ? (
          <div style={{ color: '#9B9A97' }}>暂无风险记录</div>
        ) : (
          risks.map((r, i) => (
            <div key={i} style={{ marginBottom: 12, paddingBottom: 12, borderBottom: i < risks.length - 1 ? '1px solid #f0f0f0' : 'none' }}>
              <div>
                <Tag color={SEVERITY_COLOR[r.severity]}>{SEVERITY_LABEL[r.severity]}</Tag>
                <span style={{ fontWeight: 500 }}>{r.type}</span>
                <Tag color={CONFIDENCE_COLOR[r.confidence]} style={{ marginLeft: 6 }}>
                  {CONFIDENCE_LABEL[r.confidence]}
                </Tag>
                {r.year && <span style={{ marginLeft: 8, color: '#9B9A97', fontSize: 12 }}>{r.year}</span>}
              </div>
              <div style={{ marginTop: 4, color: '#37352F' }}>{r.desc}</div>
              {r.source && <div style={{ marginTop: 2, color: '#9B9A97', fontSize: 12 }}>来源：{r.source}</div>}
              {(r.direction_tags || []).length > 0 && (
                <div style={{ marginTop: 4 }}>
                  {(r.direction_tags || []).map(t => <Tag key={t} color="orange">{t}</Tag>)}
                </div>
              )}
            </div>
          ))
        )}
      </Card>

      <Card size="small" title="推荐理由">
        <div style={{ whiteSpace: 'pre-wrap', lineHeight: 1.7 }}>{rec.reason || '—'}</div>
      </Card>
    </>
  );
};

export default RecommendationList;
