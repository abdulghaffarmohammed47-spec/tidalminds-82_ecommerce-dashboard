import React, { useState } from 'react';
import { ArrowRight } from 'lucide-react';

interface Props {
  onSearch: (query: string) => void;
}

export const HeroSearchBar: React.FC<Props> = ({ onSearch }) => {
  const [query, setQuery] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim()) onSearch(query.trim());
  };

  return (
    <form onSubmit={handleSubmit} className="relative w-full max-w-[680px] mx-auto">
      <div className="relative flex items-center bg-[#ffffff] rounded-[9999px] border border-[#000000]/10 shadow-[0_2px_8px_rgba(0,0,0,0.06)] pl-5 pr-1.5 py-1 transition-all focus-within:border-[#5433eb]">
        <input 
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="What are you shopping for today?"
          className="w-full bg-transparent text-[16px] font-['GT_Standard'] tracking-[-0.031em] text-[#000000] placeholder:text-[#787574] focus:outline-none"
        />
        <button 
          type="submit" 
          aria-label="Submit Search"
          className="w-[48px] h-[48px] rounded-[9999px] bg-[#5433eb] flex items-center justify-center text-[#ffffff] shadow-[0_4px_24px_rgba(69,36,219,0.34)] hover:brightness-110 active:scale-95 transition-all flex-shrink-0"
        >
          <ArrowRight size={18} strokeWidth={2.5}/>
        </button>
      </div>
    </form>
  );
};
