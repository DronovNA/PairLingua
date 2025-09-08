import React, { useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { Outlet } from 'react-router-dom';

import { RootState } from '@/store';
import { setSidebarOpen, updateDeviceInfo } from '@/store/appSlice';
import Header from './Header';
import Sidebar from './Sidebar';

interface LayoutProps {
  children: React.ReactNode;
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  const dispatch = useDispatch();
  const { sidebarOpen, deviceInfo } = useSelector((state: RootState) => state.app);

  useEffect(() => {
    const handleResize = () => {
      dispatch(updateDeviceInfo());
      
      // Auto-close sidebar on mobile when window is resized
      if (deviceInfo.isMobile && sidebarOpen) {
        dispatch(setSidebarOpen(false));
      }
    };

    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, [dispatch, deviceInfo.isMobile, sidebarOpen]);

  // Close sidebar when clicking outside on mobile
  const handleBackdropClick = () => {
    if (deviceInfo.isMobile && sidebarOpen) {
      dispatch(setSidebarOpen(false));
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 flex">
      {/* Sidebar */}
      <div className={`
        ${deviceInfo.isMobile 
          ? `fixed inset-y-0 left-0 z-50 w-64 transform transition-transform duration-300 ease-in-out ${
              sidebarOpen ? 'translate-x-0' : '-translate-x-full'
            }`
          : `relative ${sidebarOpen ? 'w-64' : 'w-16'} transition-all duration-300`
        }
      `}>
        <Sidebar />
      </div>

      {/* Mobile backdrop */}
      {deviceInfo.isMobile && sidebarOpen && (
        <div 
          className="fixed inset-0 z-40 bg-black bg-opacity-50 transition-opacity"
          onClick={handleBackdropClick}
        />
      )}

      {/* Main content */}
      <div className="flex-1 flex flex-col min-w-0">
        <Header />
        
        <main className="flex-1 p-4 sm:p-6 lg:p-8">
          <div className="max-w-7xl mx-auto">
            {children}
          </div>
        </main>
      </div>
    </div>
  );
};

export default Layout;
