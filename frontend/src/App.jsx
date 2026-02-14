import { useState, useEffect } from 'react'

const API_URL = '/api'

function App() {
  const [activeTab, setActiveTab] = useState('users')
  const [users, setUsers] = useState([])
  const [orders, setOrders] = useState([])
  const [error, setError] = useState(null)
  const [success, setSuccess] = useState(null)
  const [loading, setLoading] = useState(false)

  // User form state
  const [userEmail, setUserEmail] = useState('')
  const [userName, setUserName] = useState('')

  // Order form state
  const [selectedUserId, setSelectedUserId] = useState('')

  // Item form state
  const [selectedOrderId, setSelectedOrderId] = useState('')
  const [productName, setProductName] = useState('')
  const [productPrice, setProductPrice] = useState('')
  const [productQuantity, setProductQuantity] = useState('1')

  useEffect(() => {
    fetchUsers()
    fetchOrders()
  }, [])

  const showError = (msg) => {
    setError(msg)
    setSuccess(null)
    setTimeout(() => setError(null), 5000)
  }

  const showSuccess = (msg) => {
    setSuccess(msg)
    setError(null)
    setTimeout(() => setSuccess(null), 3000)
  }

  // API calls
  const fetchUsers = async () => {
    try {
      const res = await fetch(`${API_URL}/users`)
      if (res.ok) {
        setUsers(await res.json())
      }
    } catch (e) {
      console.error('Failed to fetch users:', e)
    }
  }

  const fetchOrders = async () => {
    try {
      const res = await fetch(`${API_URL}/orders`)
      if (res.ok) {
        setOrders(await res.json())
      }
    } catch (e) {
      console.error('Failed to fetch orders:', e)
    }
  }

  const createUser = async (e) => {
    e.preventDefault()
    setLoading(true)
    try {
      const res = await fetch(`${API_URL}/users`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: userEmail, name: userName }),
      })
      if (res.ok) {
        showSuccess('User created successfully!')
        setUserEmail('')
        setUserName('')
        fetchUsers()
      } else {
        const data = await res.json()
        showError(data.detail || 'Failed to create user')
      }
    } catch (e) {
      showError('Network error')
    }
    setLoading(false)
  }

  const createOrder = async (e) => {
    e.preventDefault()
    if (!selectedUserId) {
      showError('Please select a user')
      return
    }
    setLoading(true)
    try {
      const res = await fetch(`${API_URL}/orders`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id: selectedUserId }),
      })
      if (res.ok) {
        showSuccess('Order created successfully!')
        fetchOrders()
      } else {
        const data = await res.json()
        showError(data.detail || 'Failed to create order')
      }
    } catch (e) {
      showError('Network error')
    }
    setLoading(false)
  }

  const addItem = async (e) => {
    e.preventDefault()
    if (!selectedOrderId) {
      showError('Please select an order')
      return
    }
    setLoading(true)
    try {
      const res = await fetch(`${API_URL}/orders/${selectedOrderId}/items`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          product_name: productName,
          price: parseFloat(productPrice),
          quantity: parseInt(productQuantity),
        }),
      })
      if (res.ok) {
        showSuccess('Item added successfully!')
        setProductName('')
        setProductPrice('')
        setProductQuantity('1')
        fetchOrders()
      } else {
        const data = await res.json()
        showError(data.detail || 'Failed to add item')
      }
    } catch (e) {
      showError('Network error')
    }
    setLoading(false)
  }

  const payOrder = async (orderId) => {
    setLoading(true)
    try {
      const res = await fetch(`${API_URL}/orders/${orderId}/pay`, {
        method: 'POST',
      })
      if (res.ok) {
        showSuccess('Order paid successfully!')
        fetchOrders()
      } else {
        const data = await res.json()
        showError(data.detail || 'Failed to pay order')
      }
    } catch (e) {
      showError('Network error')
    }
    setLoading(false)
  }

  const cancelOrder = async (orderId) => {
    setLoading(true)
    try {
      const res = await fetch(`${API_URL}/orders/${orderId}/cancel`, {
        method: 'POST',
      })
      if (res.ok) {
        showSuccess('Order cancelled!')
        fetchOrders()
      } else {
        const data = await res.json()
        showError(data.detail || 'Failed to cancel order')
      }
    } catch (e) {
      showError('Network error')
    }
    setLoading(false)
  }

  return (
    <div className="container">
      <h1>🛒 Marketplace</h1>
      
      {error && <div className="error">{error}</div>}
      {success && <div className="success">{success}</div>}

      <div className="tabs">
        <div 
          className={`tab ${activeTab === 'users' ? 'active' : ''}`}
          onClick={() => setActiveTab('users')}
        >
          Users
        </div>
        <div 
          className={`tab ${activeTab === 'orders' ? 'active' : ''}`}
          onClick={() => setActiveTab('orders')}
        >
          Orders
        </div>
      </div>

      {activeTab === 'users' && (
        <div className="grid">
          <div className="card">
            <h2>Create User</h2>
            <form onSubmit={createUser}>
              <div className="form-group">
                <label>Email</label>
                <input
                  type="email"
                  value={userEmail}
                  onChange={(e) => setUserEmail(e.target.value)}
                  placeholder="user@example.com"
                  required
                />
              </div>
              <div className="form-group">
                <label>Name</label>
                <input
                  type="text"
                  value={userName}
                  onChange={(e) => setUserName(e.target.value)}
                  placeholder="John Doe"
                />
              </div>
              <button className="btn btn-primary" disabled={loading}>
                Create User
              </button>
            </form>
          </div>

          <div className="card">
            <h2>Users ({users.length})</h2>
            <table>
              <thead>
                <tr>
                  <th>Email</th>
                  <th>Name</th>
                </tr>
              </thead>
              <tbody>
                {users.map((user) => (
                  <tr key={user.id}>
                    <td>{user.email}</td>
                    <td>{user.name || '-'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {activeTab === 'orders' && (
        <>
          <div className="grid">
            <div className="card">
              <h2>Create Order</h2>
              <form onSubmit={createOrder}>
                <div className="form-group">
                  <label>User</label>
                  <select
                    value={selectedUserId}
                    onChange={(e) => setSelectedUserId(e.target.value)}
                    style={{ width: '100%', padding: '10px', borderRadius: '4px', border: '1px solid #ddd' }}
                  >
                    <option value="">Select user...</option>
                    {users.map((user) => (
                      <option key={user.id} value={user.id}>
                        {user.email}
                      </option>
                    ))}
                  </select>
                </div>
                <button className="btn btn-primary" disabled={loading}>
                  Create Order
                </button>
              </form>
            </div>

            <div className="card">
              <h2>Add Item to Order</h2>
              <form onSubmit={addItem}>
                <div className="form-group">
                  <label>Order</label>
                  <select
                    value={selectedOrderId}
                    onChange={(e) => setSelectedOrderId(e.target.value)}
                    style={{ width: '100%', padding: '10px', borderRadius: '4px', border: '1px solid #ddd' }}
                  >
                    <option value="">Select order...</option>
                    {orders.filter(o => o.status === 'created').map((order) => (
                      <option key={order.id} value={order.id}>
                        Order #{order.id.slice(0, 8)} - {order.total_amount}₽
                      </option>
                    ))}
                  </select>
                </div>
                <div className="form-group">
                  <label>Product Name</label>
                  <input
                    type="text"
                    value={productName}
                    onChange={(e) => setProductName(e.target.value)}
                    placeholder="iPhone 15"
                    required
                  />
                </div>
                <div className="form-group">
                  <label>Price</label>
                  <input
                    type="number"
                    step="0.01"
                    min="0"
                    value={productPrice}
                    onChange={(e) => setProductPrice(e.target.value)}
                    placeholder="99999"
                    required
                  />
                </div>
                <div className="form-group">
                  <label>Quantity</label>
                  <input
                    type="number"
                    min="1"
                    value={productQuantity}
                    onChange={(e) => setProductQuantity(e.target.value)}
                    required
                  />
                </div>
                <button className="btn btn-primary" disabled={loading}>
                  Add Item
                </button>
              </form>
            </div>
          </div>

          <div className="card">
            <h2>Orders ({orders.length})</h2>
            {orders.map((order) => (
              <div key={order.id} className="card" style={{ background: '#fafafa' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <div>
                    <strong>Order #{order.id.slice(0, 8)}</strong>
                    <span className={`status-badge status-${order.status}`} style={{ marginLeft: '12px' }}>
                      {order.status}
                    </span>
                  </div>
                  <div>
                    <strong>{order.total_amount}₽</strong>
                  </div>
                </div>
                
                {order.items && order.items.length > 0 && (
                  <div className="order-items">
                    {order.items.map((item) => (
                      <div key={item.id} className="order-item">
                        <span>{item.product_name} × {item.quantity}</span>
                        <span>{item.subtotal}₽</span>
                      </div>
                    ))}
                  </div>
                )}

                <div className="actions" style={{ marginTop: '12px' }}>
                  {order.status === 'created' && (
                    <>
                      <button 
                        className="btn btn-success" 
                        onClick={() => payOrder(order.id)}
                        disabled={loading}
                      >
                        Pay
                      </button>
                      <button 
                        className="btn btn-danger" 
                        onClick={() => cancelOrder(order.id)}
                        disabled={loading}
                      >
                        Cancel
                      </button>
                    </>
                  )}
                  {order.status === 'paid' && (
                    <span style={{ color: '#666' }}>✓ Paid - awaiting shipment</span>
                  )}
                </div>
              </div>
            ))}
          </div>
        </>
      )}
    </div>
  )
}

export default App
