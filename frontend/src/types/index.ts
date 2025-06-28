export interface User {
  id: number;
  email: string;
  role: 'mentor' | 'mentee';
  profile: UserProfile;
}

export interface UserProfile {
  name: string;
  bio: string;
  imageUrl: string;
  skills?: string[];
}

export interface SignupRequest {
  email: string;
  password: string;
  name: string;
  role: 'mentor' | 'mentee';
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface LoginResponse {
  token: string;
}

export interface ProfileUpdateRequest {
  id: number;
  name: string;
  role: 'mentor' | 'mentee';
  bio: string;
  image?: string;
  skills?: string[];
}

export interface MatchRequest {
  id: number;
  mentorId: number;
  menteeId: number;
  message: string;
  status: 'pending' | 'accepted' | 'rejected' | 'cancelled';
}

// 별칭 추가
export type MatchingRequest = MatchRequest;

export interface MatchRequestCreate {
  mentorId: number;
  menteeId: number;
  message: string;
}
