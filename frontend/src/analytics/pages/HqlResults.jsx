import React, { useState, useCallback, useMemo } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { Button, Input, Card, Badge, Spinner, SearchInput } from '@shared/ui';
import './HqlResults.css';

/**
 * HQL结果列表页面
 * 显示所有生成的HQL语句
 */
function HqlResults() {
  const [searchTerm, setSearchTerm] = useState('');

  const { data: results = [], isLoading } = useQuery({
    queryKey: ['hql-results'],
    queryFn: async () => {
      const response = await fetch('/api/hql/results');
      if (!response.ok) throw new Error('加载失败');
      return response.json();
    }
  });

  // 使用 useCallback 优化事件处理
  const handleSearchChange = useCallback((e) => {
    setSearchTerm(e.target.value);
  }, []);

  // 使用 useMemo 优化过滤逻辑
  const filteredResults = useMemo(() => {
    return results.filter(result =>
      result.event_name?.toLowerCase().includes(searchTerm.toLowerCase())
    );
  }, [results, searchTerm]);

  if (isLoading) {
    return (
      <div className="hql-results-container" data-testid="hql-results-loading">
        <div className="loading-container">
          <Spinner size="lg" label="加载HQL结果中..." />
        </div>
      </div>
    );
  }

  return (
    <div className="hql-results-container" data-testid="hql-results">
      <div className="page-header">
        <h1>HQL结果</h1>
        <Link to="/hql-manage">
          <Button variant="ghost">
            <i className="bi bi-arrow-left"></i>
            返回
          </Button>
        </Link>
      </div>

      <Card className="glass-card">
        <Card.Body>
          <div className="search-bar">
            <SearchInput
              placeholder="搜索HQL结果..."
              value={searchTerm}
              onChange={(value) => setSearchTerm(value)}
            />
          </div>

          <div className="results-list">
            {filteredResults.map(result => (
              <Card key={result.id} className="result-item glass-card">
                <Card.Body>
                  <div className="result-header">
                    <h3>{result.event_name}</h3>
                    <Badge variant="success">已生成</Badge>
                  </div>
                  <pre className="result-code">{result.hql}</pre>
                </Card.Body>
              </Card>
            ))}
          </div>
        </Card.Body>
      </Card>
    </div>
  );
}

export default React.memo(HqlResults);
