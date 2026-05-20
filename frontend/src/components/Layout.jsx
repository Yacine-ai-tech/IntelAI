import { Outlet } from 'react-router-dom'
import Sidebar from './Sidebar'
import FloatingChat from './FloatingChat'

export default function Layout() {
  return (
    <div className="layout">
      <Sidebar />
      <main className="main-content">
        <Outlet />
      </main>
      <FloatingChat />
    </div>
  )
}
