package org.jofu.bleva;

public interface POSTListener<T> {
    public void onSuccess(T object);
    public void onFail(Exception e);
}