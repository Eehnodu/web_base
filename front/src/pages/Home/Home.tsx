const Home = () => {
  return (
    <div className="w-screen h-screen flex items-center justify-center bg-gray-100">
      <div className="bg-white p-8 rounded-xl shadow-md text-center">
        <h1 className="text-3xl font-bold text-blue-600 mb-2">
          🚀 Base Project
        </h1>
        <p className="text-xl text-gray-800">
          🎉 Hello from <strong>Base Project Home</strong>
        </p>
        <p className="text-sm text-gray-500 mt-2">
          FastAPI + React + TailwindCSS
        </p>
      </div>
    </div>
  );
};

export default Home;
