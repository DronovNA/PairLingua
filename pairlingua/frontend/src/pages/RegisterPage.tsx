import React from 'react';
import { Link } from 'react-router-dom';

const RegisterPage: React.FC = () => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 to-secondary-50 flex items-center justify-center px-4">
      <div className="max-w-md w-full bg-white rounded-2xl shadow-xl p-8">
        <div className="text-center mb-8">
          <h1 className="text-2xl font-bold text-gray-900">Регистрация</h1>
          <p className="text-gray-600 mt-2">Создайте новый аккаунт</p>
        </div>
        
        <div className="text-center">
          <p className="text-gray-600">Страница в разработке</p>
          <Link to="/login" className="text-primary-600 hover:text-primary-500 font-medium">
            Вернуться к входу
          </Link>
        </div>
      </div>
    </div>
  );
};

export default RegisterPage;
