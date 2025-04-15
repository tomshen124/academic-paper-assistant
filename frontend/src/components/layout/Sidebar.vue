.sidebar {
  height: 100vh;
  background: #001529;
  color: #fff;
  
  .el-menu {
    border-right: none;
    background: transparent;
    
    .el-menu-item {
      color: rgba(255, 255, 255, 0.65);
      height: 50px;
      line-height: 50px;
      
      &:hover {
        color: #fff;
        background: #1890ff;
      }
      
      &.is-active {
        color: #fff;
        background: #1890ff;
      }
      
      i {
        color: inherit;
        font-size: 18px;
        margin-right: 10px;
      }
    }
    
    .el-submenu__title {
      color: rgba(255, 255, 255, 0.65);
      
      &:hover {
        color: #fff;
        background: #1890ff;
      }
      
      i {
        color: inherit;
      }
    }
  }
  
  .logo {
    height: 64px;
    padding: 16px;
    text-align: center;
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
    
    img {
      height: 32px;
    }
  }
} 