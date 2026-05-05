# README Kubernetes manifest

Короткий опис данного маніфесту

___


```
apiVersion: apps/v1
kind: Deployment
metadata:
  name: backend-deployment
  labels:
    app: backend

```

Опис ресурсу Deployment



```
spec:
  replicas: 2                        
  selector:
    matchLabels:
      app: backend
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxUnavailable: 1              
      maxSurge: 1

```
Створення 2 контейнерів, при випадку якшо один контейнер упав ми піднімаємо інший(дальше розглянемо), це є основною ціллю цього кубернетіс файлу

```
livenessProbe:
            httpGet:
              path: /
              port: 80
            initialDelaySeconds: 10
            periodSeconds: 5
            failureThreshold: 3
```
Перевірка чи живий контейнер

```
readinessProbe:
            httpGet:
              path: /
              port: 80
            initialDelaySeconds: 5
            periodSeconds: 3
```

Чи готовий контейнер приймати запити

```
resources:
  requests:
    memory: "64Mi"
    cpu: "100m"
  limits:
    memory: "128Mi"
    cpu: "250m"
```

Ресурси які ми виділяємо

___

Це основна інформація яку треба було пояснити, так як ТЗ не було конкретним, було створено тільки базу,
адже бек в данному випадку не був крепко великим, як би, бек був більше потрібно було б по правильному розподілити кожен сервіс бека, на кожен окремий контейнер, після чого по правильній архітектурі це були би мікросервіси які були б незалежними один від одного, і потребували б для кожного окремого мікросервіса свій хостинг









