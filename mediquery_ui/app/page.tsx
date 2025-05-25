'use client';
import React, { useState } from 'react';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Loader2 } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Skeleton } from '@/components/ui/skeleton';

interface QueryResult {
  topic: string;
  domain_filter: string[];
  answer: string;
  citations: string[];
}

const formatAnswerWithCitations = (answer: string, citations: string[]) => {
  let formattedAnswer = answer;
  citations.forEach((citation, index) => {
    // Replace [n] with a linked citation
    formattedAnswer = formattedAnswer.replace(
      `[${index + 1}]`,
      `[[${index + 1}]](${citation})`
    );
  });
  return formattedAnswer;
};

const LoadingSkeleton = () => (
  <Card className="mt-6">
    <CardContent className="space-y-4">
      <div className="space-y-2">
        <Skeleton className="h-4 w-3/4" />
        <Skeleton className="h-4 w-1/2" />
      </div>
      <div className="space-y-2">
        <Skeleton className="h-4 w-full" />
        <Skeleton className="h-4 w-full" />
        <Skeleton className="h-4 w-5/6" />
      </div>
      <div className="space-y-2">
        <Skeleton className="h-4 w-full" />
        <Skeleton className="h-4 w-4/5" />
        <Skeleton className="h-4 w-full" />
      </div>
      <div className="space-y-2 pt-4 border-t">
        <Skeleton className="h-3 w-24" />
        <div className="space-y-1">
          <Skeleton className="h-3 w-2/3" />
          <Skeleton className="h-3 w-3/4" />
          <Skeleton className="h-3 w-1/2" />
        </div>
      </div>
    </CardContent>
  </Card>
);

export default function MediQueryUI() {
  const [question, setQuestion] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<QueryResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const askQuestion = async () => {
    if (!question.trim()) return;
    
    setLoading(true);
    setResult(null);
    setError(null);

    try {
      const res = await fetch('http://127.0.0.1:8000/ask', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ question }),
      });

      if (!res.ok) {
        throw new Error(`HTTP error! Status: ${res.status}`);
      }

      const data = await res.json();
      setResult(data);
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      askQuestion();
    }
  };

  return (
    <div className="max-w-4xl mx-auto py-12 px-4">
      <h1 className="text-3xl font-bold mb-6 text-center">MediQuery</h1>
      <div className="flex gap-4 mb-6">
        <Input
          placeholder="Ask a medical question..."
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          onKeyDown={handleKeyPress}
        />
        <Button 
          onClick={askQuestion} 
          disabled={loading || !question.trim()}
          className="min-w-[80px]"
        >
          {loading ? <Loader2 className="animate-spin" /> : 'Ask'}
        </Button>
      </div>

      {error && (
        <div className="p-4 mb-6 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-red-600">Error: {error}</p>
        </div>
      )}

      {loading && <LoadingSkeleton />}

      {!loading && result && (
        <Card className="mt-6">
          <CardContent className="space-y-4 prose prose-slate max-w-none">
            <ReactMarkdown remarkPlugins={[remarkGfm]}>
              {formatAnswerWithCitations(result.answer, result.citations)}
            </ReactMarkdown>
            <div className="mt-4 pt-4 border-t">
              <h3 className="text-sm font-semibold text-gray-500">Sources:</h3>
              <ul className="list-decimal list-inside text-sm text-blue-700">
                {result.citations.map((cite, i) => (
                  <li key={i}><a href={cite} target="_blank" rel="noopener noreferrer">{cite}</a></li>
                ))}
              </ul>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
} 

