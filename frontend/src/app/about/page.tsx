'use client';

import { UserGroupIcon, AcademicCapIcon, CodeBracketIcon } from '@heroicons/react/24/outline';
import Image from 'next/image'

const teamMembers = [
  {
    name: 'Krish Chhajer',
    role: 'Frontend Developer',
    image: '/images/team/krish.jpg',
    bio: 'Specialized in React and Next.js development.'
  },
  {
    name: 'Kenny Guo',
    role: 'Backend Developer',
    image: '/images/team/kenny.jpg',
    bio: 'Expert in Python and microservices architecture.'
  },
  {
    name: 'Luthira Abeykoon',
    role: 'Data Scientist',
    image: '/images/team/luthira.jpg',
    bio: 'Focuses on machine learning and data analysis.'
  },
  {
    name: 'Nick Eckhert',
    role: 'DevOps Engineer',
    image: '/images/team/nick.jpg',
    bio: 'Handles deployment and infrastructure management.'
  }
];

const mentor = {
  name: 'Dr. Robert Chen',
  role: 'Project Mentor',
  image: '/images/team/robert.jpg',
  bio: 'Professor of Electrical Engineering with expertise in smart grid systems.'
};

const features = [
  {
    title: 'Expert Team',
    description: 'Our team consists of experienced professionals in energy systems, software development, and user experience design.',
    icon: UserGroupIcon
  },
  {
    title: 'Academic Excellence',
    description: 'We combine academic research with practical implementation to deliver cutting-edge solutions.',
    icon: AcademicCapIcon
  },
  {
    title: 'Technical Innovation',
    description: 'Leveraging the latest technologies to build robust and scalable microgrid management systems.',
    icon: CodeBracketIcon
  }
];

export default function About() {
  return (
    <main className="min-h-screen p-8">
      <div className="max-w-7xl mx-auto">
        <h1 className="text-3xl font-bold text-gray-900 mb-8">About Our Team</h1>
        
        {/* Developers Section */}
        <div className="mb-12">
          <h2 className="text-2xl font-semibold text-gray-800 mb-6">Development Team</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
            {teamMembers.map((member) => (
              <div key={member.name} className="bg-white rounded-lg shadow p-6">
                <div className="relative w-32 h-32 mx-auto mb-4">
                  <Image
                    src={member.image}
                    alt={member.name}
                    fill
                    className="rounded-full object-cover"
                  />
                </div>
                <h3 className="text-xl font-semibold text-gray-900 text-center">{member.name}</h3>
                <p className="text-gray-600 text-center mb-2">{member.role}</p>
                <p className="text-gray-500 text-sm text-center">{member.bio}</p>
              </div>
            ))}
          </div>
        </div>

        {/* Mentor Section */}
        <div>
          <h2 className="text-2xl font-semibold text-gray-800 mb-6">Project Mentor</h2>
          <div className="bg-white rounded-lg shadow p-6 max-w-2xl mx-auto">
            <div className="flex flex-col items-center">
              <div className="relative w-40 h-40 mb-4">
                <Image
                  src={mentor.image}
                  alt={mentor.name}
                  fill
                  className="rounded-full object-cover"
                />
              </div>
              <h3 className="text-2xl font-semibold text-gray-900 text-center">{mentor.name}</h3>
              <p className="text-gray-600 text-center mb-2">{mentor.role}</p>
              <p className="text-gray-500 text-center">{mentor.bio}</p>
            </div>
          </div>
        </div>
      </div>
    </main>
  );
} 