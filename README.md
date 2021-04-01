# 跨学科论文识别
每一篇论文会有可能在多个学科产生影响，本项目假设一篇论文有其唯一的原生领域original field，表示为I_0，并且会在其他的field产生影响,I_t。

那么本文假设跨学科影响力转化率为(Iter-disciplinary Impact Translation Rate)
    
    IITR(I_0,I_t) = \frac{I_t}{I_0}

本文该转化率与领域间相关性，

    IITR(I_0,I_t) \propto R(T_0,T_t)


## 领域相似度计算
领域相似度等于一个主题对于另一个主题的有用层度。
m_ij = \frac{t_j -> t_i}{t_j -> *}
领域i对于j的相似度等于领域j引用领域i的引用总次数，比上领域j引用总次数。
因此基于引用关系的领域相似度不是一个对称变量。

