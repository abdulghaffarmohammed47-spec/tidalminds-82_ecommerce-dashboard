import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { Mail, Lock, User, AlertCircle, Sparkles } from 'lucide-react';
import api from '../lib/api';
import { useAuthStore } from '../store/authStore';

export const Register: React.FC = () => {
  const [fullName, setFullName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();
  const setAuth = useAuthStore((state) => state.setAuth);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');

    try {
      await api.post('/api/auth/register', {
        email,
        password,
        full_name: fullName,
        role: 'CUSTOMER'
      });

      // Auto login after registration
      const loginRes = await api.post('/api/auth/login', {
        email,
        password
      });

      const token = loginRes.data.access_token;
      setAuth({ id: 'me', email, full_name: fullName, role: 'CUSTOMER' }, token);
      navigate('/');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to register account');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex justify-center items-center min-h-[calc(100vh-14rem)] px-4 py-8">
      <div className="bg-[#ffffff] rounded-[28px] p-8 w-full max-w-md border border-[#ebebeb] shadow-[0_4px_6px_-1px_rgba(0,0,0,0.1),0_2px_4px_-2px_rgba(0,0,0,0.1)] space-y-6">
        
        <div className="text-center space-y-2">
          <div className="w-12 h-12 rounded-[9999px] bg-[#5433eb] text-[#ffffff] flex items-center justify-center mx-auto shadow-[0_4px_24px_rgba(69,36,219,0.34)]">
            <Sparkles size={22} />
          </div>
          <h2 className="text-2xl font-bold tracking-[-0.05em] text-[#000000]">Create Account</h2>
          <p className="text-[13px] tracking-[-0.017em] text-[#787574]">
            Join SmartCommerce AI on white marble
          </p>
        </div>

        {error && (
          <div className="bg-red-50 border border-red-200 text-red-600 p-3 rounded-[16px] flex items-center gap-2 text-[12px] font-medium tracking-[-0.017em]">
            <AlertCircle className="w-4 h-4 flex-shrink-0" />
            <p>{error}</p>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-1">
            <label className="text-[12px] font-semibold tracking-[-0.017em] text-[#000000]">Full Name</label>
            <div className="relative">
              <User className="w-4 h-4 absolute left-3.5 top-1/2 transform -translate-y-1/2 text-[#787574]" />
              <input
                type="text"
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                className="w-full bg-[#f2f4f5] rounded-[9999px] px-4 py-2.5 pl-10 text-[13px] tracking-[-0.017em] text-[#000000] placeholder:text-[#787574] focus:outline-none focus:ring-2 focus:ring-[#5433eb]/40 focus:bg-[#ffffff] transition-all"
                placeholder="Alex Morgan"
                required
              />
            </div>
          </div>

          <div className="space-y-1">
            <label className="text-[12px] font-semibold tracking-[-0.017em] text-[#000000]">Email Address</label>
            <div className="relative">
              <Mail className="w-4 h-4 absolute left-3.5 top-1/2 transform -translate-y-1/2 text-[#787574]" />
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full bg-[#f2f4f5] rounded-[9999px] px-4 py-2.5 pl-10 text-[13px] tracking-[-0.017em] text-[#000000] placeholder:text-[#787574] focus:outline-none focus:ring-2 focus:ring-[#5433eb]/40 focus:bg-[#ffffff] transition-all"
                placeholder="alex@example.com"
                required
              />
            </div>
          </div>

          <div className="space-y-1">
            <label className="text-[12px] font-semibold tracking-[-0.017em] text-[#000000]">Password</label>
            <div className="relative">
              <Lock className="w-4 h-4 absolute left-3.5 top-1/2 transform -translate-y-1/2 text-[#787574]" />
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full bg-[#f2f4f5] rounded-[9999px] px-4 py-2.5 pl-10 text-[13px] tracking-[-0.017em] text-[#000000] placeholder:text-[#787574] focus:outline-none focus:ring-2 focus:ring-[#5433eb]/40 focus:bg-[#ffffff] transition-all"
                placeholder="••••••••"
                required
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={isLoading}
            className="w-full py-3 bg-[#5433eb] hover:brightness-110 active:scale-[0.98] text-[#ffffff] rounded-[9999px] text-[14px] font-semibold tracking-[-0.014em] shadow-[0_4px_24px_rgba(69,36,219,0.34)] transition-all cursor-pointer mt-2"
          >
            {isLoading ? 'Creating Account...' : 'Create Account'}
          </button>
        </form>

        <div className="text-center text-[12px] tracking-[-0.017em] text-[#787574]">
          Already have an account?{' '}
          <Link to="/login" className="text-[#5433eb] font-semibold hover:underline">
            Sign In
          </Link>
        </div>

      </div>
    </div>
  );
};
export default Register;
