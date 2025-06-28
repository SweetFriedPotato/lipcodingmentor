import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { authService } from '../services/api';
import { ProfileUpdateRequest } from '../types';
import './Auth.css';

const Profile: React.FC = () => {
  const { user, updateUser } = useAuth();
  const [formData, setFormData] = useState<ProfileUpdateRequest>({
    id: 0,
    name: '',
    role: 'mentee',
    bio: '',
    image: '',
    skills: [],
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [imageFile, setImageFile] = useState<File | null>(null);
  const [skillsText, setSkillsText] = useState('');

  useEffect(() => {
    if (user) {
      setFormData({
        id: user.id,
        name: user.profile.name,
        role: user.role,
        bio: user.profile.bio,
        skills: user.profile.skills || [],
      });
      setSkillsText((user.profile.skills || []).join(', '));
    }
  }, [user]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSkillsChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const value = e.target.value;
    setSkillsText(value);
    const skillsArray = value.split(',').map(skill => skill.trim()).filter(skill => skill.length > 0);
    setFormData(prev => ({
      ...prev,
      skills: skillsArray
    }));
  };

  const handleImageChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      if (file.size > 1024 * 1024) {
        setError('이미지 크기는 1MB 이하여야 합니다.');
        return;
      }
      if (!['image/jpeg', 'image/png'].includes(file.type)) {
        setError('JPG 또는 PNG 형식만 지원됩니다.');
        return;
      }
      setImageFile(file);
      setError('');
    }
  };

  const convertImageToBase64 = (file: File): Promise<string> => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = () => {
        const result = reader.result as string;
        const base64 = result.split(',')[1];
        resolve(base64);
      };
      reader.onerror = reject;
      reader.readAsDataURL(file);
    });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setSuccess('');

    try {
      let imageBase64 = '';
      if (imageFile) {
        imageBase64 = await convertImageToBase64(imageFile);
      }

      const updateData: ProfileUpdateRequest = {
        ...formData,
        image: imageBase64 || undefined,
      };

      const updatedUser = await authService.updateProfile(updateData);
      updateUser(updatedUser);
      setSuccess('프로필이 성공적으로 업데이트되었습니다.');
    } catch (err: any) {
      setError(err.response?.data?.detail || '프로필 업데이트에 실패했습니다.');
    } finally {
      setLoading(false);
    }
  };

  if (!user) {
    return <div>로딩 중...</div>;
  }

  return (
    <div className="profile-container">
      <div style={{ textAlign: 'center', marginBottom: '2rem' }}>
        <h1 style={{ color: 'var(--text-primary)', marginBottom: '0.5rem' }}>
          👤 내 프로필
        </h1>
        <p style={{ color: 'var(--text-secondary)' }}>
          {user.role === 'mentor' ? '멘토 정보를 관리하세요' : '멘티 정보를 관리하세요'}
        </p>
      </div>
      
      <div className="form-container">
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <img
              id="profile-photo"
              src={`http://localhost:8000${user.profile.imageUrl}`}
              alt="프로필"
              className="profile-photo"
            />
          </div>
          
          <div className="form-group">
            <label>프로필 이미지:</label>
            <input
              id="profile"
              type="file"
              accept="image/jpeg,image/png"
              onChange={handleImageChange}
            />
            <small>JPG 또는 PNG 형식, 1MB 이하, 500x500 ~ 1000x1000 픽셀</small>
          </div>
          
          <div className="form-group">
            <label>이름:</label>
            <input
              id="name"
              type="text"
              name="name"
              value={formData.name}
              onChange={handleChange}
              required
            />
          </div>
          
          <div className="form-group">
            <label>자기소개:</label>
            <textarea
              id="bio"
              name="bio"
              value={formData.bio}
              onChange={handleChange}
              rows={4}
              placeholder="자신을 소개해주세요..."
            />
          </div>
          
          {user.role === 'mentor' && (
            <div className="form-group">
              <label>기술 스택:</label>
              <textarea
                id="skillsets"
                value={skillsText}
                onChange={handleSkillsChange}
                rows={3}
                placeholder="예: React, Node.js, Python (쉼표로 구분)"
                className="skills-input"
              />
            </div>
          )}
          
          {error && <div className="error-message">{error}</div>}
          {success && <div className="success-message">{success}</div>}
          
          <button id="save" className="btn-primary" type="submit" disabled={loading}>
            {loading ? '💾 저장 중...' : '💾 저장'}
          </button>
        </form>
      </div>
    </div>
  );
};

export default Profile;
