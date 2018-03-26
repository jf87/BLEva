package org.jofu.bleva;

public interface GETListener<T> {
    public void onSuccess(T object);
    public void onFail(Exception e);
}
